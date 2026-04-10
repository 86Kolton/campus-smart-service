from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import delete, func, select, update

from app.core.database import SessionLocal
from app.models.comment import Comment
from app.models.comment_asset import CommentAsset
from app.models.comment_like import CommentLike
from app.models.message import MessageNotification
from app.models.post import Post
from app.models.user import User
from app.services.evolution_realtime_service import evolution_realtime_service
from app.services.user_service import user_service


def _format_relative(dt: datetime | None) -> str:
    if not dt:
        return "刚刚"
    now = datetime.now(tz=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    delta = now - dt
    sec = int(delta.total_seconds())
    if sec < 60:
        return "刚刚"
    minutes = sec // 60
    if minutes < 60:
        return f"{minutes} 分钟前"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} 小时前"
    days = hours // 24
    return f"{days} 天前"


def _parse_post_id(post_id: str) -> int:
    return int(str(post_id).replace("p-", ""))


def _parse_comment_id(comment_id: str) -> int:
    return int(str(comment_id).replace("c-", ""))


def _sanitize_reply_author(value: str | None) -> str | None:
    text = str(value or "").strip()
    if text.startswith("@"):
        text = text[1:]
    text = text.strip()
    return text[:60] if text else None


def _comment_notification_content(comment: Comment) -> str:
    body = str(comment.content or "").replace("\n", " ").strip()
    if not body:
        body = "图片评论"
    suffix = "..." if len(body) > 48 else ""
    return f"评论赞：{body[:48]}{suffix}"


class CommentService:
    def list_comments(self, post_id: str, user_id: int) -> list[dict]:
        try:
            raw_post_id = _parse_post_id(post_id)
        except ValueError:
            return []

        with SessionLocal() as db:
            post = db.get(Post, raw_post_id)
            post_author_id = int(post.author_id) if post else 0
            stmt = (
                select(Comment, User)
                .join(User, User.id == Comment.author_id)
                .where(Comment.post_id == raw_post_id, Comment.status == "visible")
                .order_by(Comment.id.asc())
            )
            rows = db.execute(stmt).all()
            comment_ids = [int(comment.id) for comment, _ in rows]
            image_map: dict[int, str] = {}
            if comment_ids:
                assets = db.execute(
                    select(CommentAsset).where(CommentAsset.comment_id.in_(comment_ids)).order_by(CommentAsset.id.asc())
                ).scalars().all()
                for asset in assets:
                    image_map.setdefault(int(asset.comment_id), asset.public_url)

            liked_ids: set[int] = set()
            if comment_ids:
                liked_rows = db.execute(
                    select(CommentLike.comment_id).where(
                        CommentLike.comment_id.in_(comment_ids),
                        CommentLike.user_id == int(user_id),
                    )
                ).all()
                liked_ids = {int(row[0]) for row in liked_rows}

            items = []
            for comment, user in rows:
                author_name = user_service.get_public_name(user)
                reply_to_name = str(comment.reply_to_user_name or "").strip()
                author_id = int(comment.author_id)
                items.append(
                    {
                        "id": f"c-{comment.id}",
                        "author_id": author_id,
                        "author": f"@{author_name}",
                        "content": comment.content,
                        "time": _format_relative(comment.created_at),
                        "created_at": comment.created_at.isoformat() if comment.created_at else None,
                        "image_url": image_map.get(int(comment.id)),
                        "likes": int(comment.likes_count or 0),
                        "liked": int(comment.id) in liked_ids,
                        "parent_comment_id": f"c-{int(comment.parent_comment_id)}"
                        if comment.parent_comment_id
                        else None,
                        "reply_to_author": f"@{reply_to_name}" if reply_to_name else None,
                        "can_delete": bool(author_id == int(user_id) or post_author_id == int(user_id)),
                    }
                )
            return items

    def create_comment(
        self,
        post_id: str,
        content: str,
        client_id: str | None,
        user_id: int,
        image_meta: dict | None = None,
        reply_to_comment_id: str | None = None,
        reply_to_author: str | None = None,
    ) -> dict:
        _ = client_id
        try:
            raw_post_id = _parse_post_id(post_id)
        except ValueError:
            raise ValueError("post_not_found")

        safe_content = str(content or "").strip()[:500]
        if not safe_content and not image_meta:
            raise ValueError("comment_content_required")

        with SessionLocal() as db:
            post = db.get(Post, raw_post_id)
            if not post:
                raise ValueError("post_not_found")

            parent_comment_id: int | None = None
            reply_to_author_id: int | None = None
            reply_to_user_name: str | None = None

            if reply_to_comment_id:
                try:
                    parent_comment_id = _parse_comment_id(reply_to_comment_id)
                except ValueError:
                    raise ValueError("invalid_reply_target")

                target = db.get(Comment, parent_comment_id)
                if not target or int(target.post_id) != raw_post_id:
                    raise ValueError("comment_not_found")

                reply_to_author_id = int(target.author_id)
                target_user = db.get(User, int(target.author_id))
                fallback_name = user_service.get_public_name(target_user)
                reply_to_user_name = _sanitize_reply_author(reply_to_author) or fallback_name

            next_id = int(db.scalar(select(func.max(Comment.id))) or 0) + 1
            row = Comment(
                id=next_id,
                post_id=raw_post_id,
                author_id=int(user_id),
                parent_comment_id=parent_comment_id,
                reply_to_author_id=reply_to_author_id,
                reply_to_user_name=reply_to_user_name,
                content=safe_content,
                status="visible",
                likes_count=0,
            )
            db.add(row)

            image_url = None
            if image_meta:
                next_asset_id = int(db.scalar(select(func.max(CommentAsset.id))) or 0) + 1
                asset = CommentAsset(
                    id=next_asset_id,
                    comment_id=next_id,
                    file_name=str(image_meta.get("file_name", "")),
                    file_size=int(image_meta.get("file_size", 0)),
                    mime_type=str(image_meta.get("mime_type", "")),
                    storage_path=str(image_meta.get("storage_path", "")),
                    public_url=str(image_meta.get("public_url", "")),
                )
                db.add(asset)
                image_url = asset.public_url

            post.comments_count = int(post.comments_count or 0) + 1
            db.add(post)
            db.commit()
            db.refresh(row)
            evolution_realtime_service.notify_candidate(
                post_id=raw_post_id,
                likes_count=int(post.likes_count or 0),
                comments_count=int(post.comments_count or 0),
                adopted=bool(post.adopted),
                reason="comment_count_threshold",
            )

            author_user = db.get(User, int(user_id))
            return {
                "id": f"c-{row.id}",
                "author_id": int(user_id),
                "author": f"@{user_service.get_public_name(author_user)}",
                "content": row.content,
                "time": "刚刚",
                "created_at": row.created_at.isoformat() if row.created_at else None,
                "image_url": image_url,
                "likes": int(row.likes_count or 0),
                "liked": False,
                "parent_comment_id": f"c-{int(row.parent_comment_id)}" if row.parent_comment_id else None,
                "reply_to_author": f"@{row.reply_to_user_name}" if row.reply_to_user_name else None,
                "can_delete": True,
            }

    def toggle_comment_like(self, comment_id: str, liked: bool, user_id: int) -> dict:
        try:
            raw_comment_id = _parse_comment_id(comment_id)
        except ValueError as exc:
            raise ValueError("comment_not_found") from exc

        with SessionLocal() as db:
            comment = db.get(Comment, raw_comment_id)
            if not comment or comment.status != "visible":
                raise ValueError("comment_not_found")

            existing = db.execute(
                select(CommentLike).where(
                    CommentLike.comment_id == raw_comment_id,
                    CommentLike.user_id == int(user_id),
                )
            ).scalar_one_or_none()

            if liked:
                if not existing:
                    next_id = int(db.scalar(select(func.max(CommentLike.id))) or 0) + 1
                    db.add(CommentLike(id=next_id, comment_id=raw_comment_id, user_id=int(user_id)))
                    comment.likes_count = int(comment.likes_count or 0) + 1
                    db.add(comment)
                    content = _comment_notification_content(comment)
                    notification = db.execute(
                        select(MessageNotification).where(
                            MessageNotification.receiver_user_id == int(comment.author_id),
                            MessageNotification.type == "likes",
                            MessageNotification.source_post_id == int(comment.post_id),
                            MessageNotification.source_user_id == int(user_id),
                            MessageNotification.content == content,
                        )
                    ).scalar_one_or_none()
                    if not notification:
                        next_notice_id = int(db.scalar(select(func.max(MessageNotification.id))) or 0) + 1
                        db.add(
                            MessageNotification(
                                id=next_notice_id,
                                receiver_user_id=int(comment.author_id),
                                type="likes",
                                source_post_id=int(comment.post_id),
                                source_user_id=int(user_id),
                                content=content,
                                is_read=False,
                            )
                        )
            else:
                if existing:
                    db.execute(
                        delete(CommentLike).where(
                            CommentLike.comment_id == raw_comment_id,
                            CommentLike.user_id == int(user_id),
                        )
                    )
                    comment.likes_count = max(0, int(comment.likes_count or 0) - 1)
                    db.add(comment)
                    db.execute(
                        delete(MessageNotification).where(
                            MessageNotification.receiver_user_id == int(comment.author_id),
                            MessageNotification.type == "likes",
                            MessageNotification.source_post_id == int(comment.post_id),
                            MessageNotification.source_user_id == int(user_id),
                            MessageNotification.content == _comment_notification_content(comment),
                        )
                    )

            db.commit()
            db.refresh(comment)
            is_liked = (
                db.execute(
                    select(CommentLike).where(
                        CommentLike.comment_id == raw_comment_id,
                        CommentLike.user_id == int(user_id),
                    )
                ).scalar_one_or_none()
                is not None
            )
            return {
                "comment_id": f"c-{raw_comment_id}",
                "liked": bool(is_liked),
                "likes": int(comment.likes_count or 0),
            }

    def delete_comment(self, post_id: str, comment_id: str, user_id: int) -> dict:
        try:
            raw_post_id = _parse_post_id(post_id)
            raw_comment_id = _parse_comment_id(comment_id)
        except ValueError as exc:
            raise ValueError("comment_not_found") from exc

        with SessionLocal() as db:
            post = db.get(Post, raw_post_id)
            if not post:
                raise ValueError("post_not_found")

            comment = db.get(Comment, raw_comment_id)
            if not comment or int(comment.post_id) != raw_post_id:
                raise ValueError("comment_not_found")

            is_owner = int(post.author_id) == int(user_id)
            is_author = int(comment.author_id) == int(user_id)
            if not (is_owner or is_author):
                raise ValueError("comment_delete_forbidden")

            rows = db.execute(
                select(Comment.id, Comment.parent_comment_id, Comment.status).where(Comment.post_id == raw_post_id)
            ).all()

            children: dict[int, list[int]] = {}
            for cid, parent_cid, _status in rows:
                if parent_cid is None:
                    continue
                children.setdefault(int(parent_cid), []).append(int(cid))

            target_ids: set[int] = set()
            stack: list[int] = [raw_comment_id]
            while stack:
                current = stack.pop()
                if current in target_ids:
                    continue
                target_ids.add(current)
                stack.extend(children.get(current, []))

            deleted_count = 0
            if target_ids:
                result = db.execute(
                    update(Comment)
                    .where(
                        Comment.post_id == raw_post_id,
                        Comment.id.in_(list(target_ids)),
                        Comment.status == "visible",
                    )
                    .values(status="hidden")
                )
                deleted_count = int(result.rowcount or 0)
                db.execute(delete(CommentAsset).where(CommentAsset.comment_id.in_(list(target_ids))))
                db.execute(delete(CommentLike).where(CommentLike.comment_id.in_(list(target_ids))))

            visible_count = int(
                db.scalar(
                    select(func.count())
                    .select_from(Comment)
                    .where(Comment.post_id == raw_post_id, Comment.status == "visible")
                )
                or 0
            )
            post.comments_count = visible_count
            db.add(post)
            db.commit()
            return {
                "post_id": f"p-{raw_post_id}",
                "comment_id": f"c-{raw_comment_id}",
                "deleted": True,
                "deleted_count": max(1, deleted_count),
                "deleted_ids": [f"c-{cid}" for cid in sorted(target_ids)],
            }


comment_service = CommentService()
