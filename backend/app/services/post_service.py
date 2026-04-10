from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select, update

from app.core.database import SessionLocal
from app.models.comment import Comment
from app.models.comment_asset import CommentAsset
from app.models.comment_like import CommentLike
from app.models.message import MessageNotification
from app.models.post import Post
from app.models.post_adoption import PostAdoption
from app.models.post_asset import PostAsset
from app.models.evolution_review import EvolutionReview
from app.models.post_like import PostLike
from app.models.post_save import PostSave
from app.models.user import User
from app.services.evolution_realtime_service import evolution_realtime_service
from app.services.user_service import user_service


AUTHOR_LEVEL = {
    "清晨图书馆人": "Lv.4",
    "二食堂探店组": "Lv.3",
    "课表救援队": "Lv.5",
    "考研作战组": "Lv.2",
}


def _post_notification_content(post: Post) -> str:
    title = str(post.title or "").strip() or "帖子"
    suffix = "..." if len(title) > 60 else ""
    return f"帖子赞：{title[:60]}{suffix}"


def _relative_time(dt: datetime | None) -> str:
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


class PostService:
    def _load_knowledge_ready_map(self, db, post_ids: list[int]) -> dict[int, bool]:
        if not post_ids:
            return {}

        rows = (
            db.execute(
                select(EvolutionReview)
                .where(EvolutionReview.post_id.in_(post_ids))
                .order_by(EvolutionReview.post_id.asc(), EvolutionReview.id.desc())
            )
            .scalars()
            .all()
        )
        latest: dict[int, bool] = {}
        for row in rows:
            post_id = int(row.post_id or 0)
            if not post_id or post_id in latest:
                continue
            latest[post_id] = str(row.decision or "").strip().lower() == "pass"
        return latest

    def _load_knowledge_review_map(self, db, post_ids: list[int]) -> dict[int, dict[str, str]]:
        if not post_ids:
            return {}

        rows = (
            db.execute(
                select(EvolutionReview)
                .where(EvolutionReview.post_id.in_(post_ids))
                .order_by(EvolutionReview.post_id.asc(), EvolutionReview.id.desc())
            )
            .scalars()
            .all()
        )
        latest: dict[int, dict[str, str]] = {}
        for row in rows:
            post_id = int(row.post_id or 0)
            if not post_id or post_id in latest:
                continue
            latest[post_id] = {
                "decision": str(row.decision or "").strip().lower(),
                "reason": str(row.reason or "").strip(),
            }
        return latest

    def _post_to_item(
        self,
        post: Post,
        author_name: str,
        image_url: str | None = None,
        comments_preview: list[str] | None = None,
        liked: bool = False,
        saved: bool = False,
        knowledge_ready: bool = False,
        knowledge_review_decision: str = "",
        knowledge_review_reason: str = "",
        can_delete: bool = False,
    ) -> dict:
        tags = []
        try:
            parsed = json.loads(post.tags_json or "[]")
            if isinstance(parsed, list):
                tags = [str(x) for x in parsed]
        except Exception:
            tags = []

        display_name = author_name or "匿名用户"
        return {
            "id": f"p-{post.id}",
            "category": post.category,
            "author_id": int(post.author_id),
            "author": f"@{display_name}",
            "avatar": display_name[:2] or "用户",
            "level": AUTHOR_LEVEL.get(display_name, "Lv.3"),
            "time": _relative_time(post.created_at),
            "title": post.title,
            "content": post.content,
            "tags": tags,
            "likes": int(post.likes_count or 0),
            "comments": int(post.comments_count or 0),
            "liked": bool(liked),
            "saved": bool(saved),
            "commented": False,
            "adopted": bool(post.adopted),
            "knowledge_ready": bool(knowledge_ready),
            "knowledge_review_decision": str(knowledge_review_decision or ""),
            "knowledge_review_reason": str(knowledge_review_reason or ""),
            "image_url": image_url,
            "comments_preview": comments_preview or [],
            "can_delete": bool(can_delete),
        }

    def list_posts(self, filter_name: str, user_id: int) -> list[dict]:
        with SessionLocal() as db:
            stmt = (
                select(Post, User)
                .join(User, User.id == Post.author_id)
                .where(Post.status == "published")
                .order_by(Post.id.desc())
            )
            if filter_name != "all":
                stmt = stmt.where(Post.category == filter_name)
            rows = db.execute(stmt).all()

            post_ids = [int(row[0].id) for row in rows]
            image_map: dict[int, str] = {}
            if post_ids:
                assets = db.execute(
                    select(PostAsset).where(PostAsset.post_id.in_(post_ids)).order_by(PostAsset.id.asc())
                ).scalars().all()
                for asset in assets:
                    image_map.setdefault(int(asset.post_id), asset.public_url)

            preview_map: dict[int, list[str]] = {}
            if post_ids:
                comment_rows = db.execute(
                    select(Comment, User)
                    .join(User, User.id == Comment.author_id)
                    .where(Comment.post_id.in_(post_ids), Comment.status == "visible")
                    .order_by(Comment.id.asc())
                ).all()
                for comment, comment_user in comment_rows:
                    author = user_service.get_public_name(comment_user)
                    reply_to = str(comment.reply_to_user_name or "").strip()
                    content = str(comment.content or "").replace("\n", " ").strip()
                    prefix = f"{author} 回复 @{reply_to}：" if reply_to else f"{author}："
                    line = f"{prefix}{content}"[:96]
                    bucket = preview_map.setdefault(int(comment.post_id), [])
                    bucket.append(line)
                    if len(bucket) > 3:
                        preview_map[int(comment.post_id)] = bucket[-3:]

            liked_ids: set[int] = set()
            if post_ids:
                liked_rows = db.execute(
                    select(PostLike.post_id).where(
                        PostLike.post_id.in_(post_ids),
                        PostLike.user_id == int(user_id),
                    )
                ).all()
                liked_ids = {int(row[0]) for row in liked_rows}

            saved_ids: set[int] = set()
            if post_ids:
                saved_rows = db.execute(
                    select(PostSave.post_id).where(
                        PostSave.post_id.in_(post_ids),
                        PostSave.user_id == int(user_id),
                    )
                ).all()
                saved_ids = {int(row[0]) for row in saved_rows}

            knowledge_ready_map = self._load_knowledge_ready_map(db, post_ids)
            knowledge_review_map = self._load_knowledge_review_map(db, post_ids)

            return [
                self._post_to_item(
                    post=row[0],
                    author_name=user_service.get_public_name(row[1]),
                    image_url=image_map.get(int(row[0].id)),
                    comments_preview=preview_map.get(int(row[0].id), []),
                    liked=int(row[0].id) in liked_ids,
                    saved=int(row[0].id) in saved_ids,
                    knowledge_ready=knowledge_ready_map.get(int(row[0].id), False),
                    knowledge_review_decision=knowledge_review_map.get(int(row[0].id), {}).get("decision", ""),
                    knowledge_review_reason=knowledge_review_map.get(int(row[0].id), {}).get("reason", ""),
                    can_delete=int(row[0].author_id) == int(user_id),
                )
                for row in rows
            ]

    def get_post(self, post_id: str, user_id: int) -> dict | None:
        try:
            raw_post_id = _parse_post_id(post_id)
        except ValueError:
            return None

        with SessionLocal() as db:
            row = db.execute(
                select(Post, User)
                .join(User, User.id == Post.author_id)
                .where(Post.id == raw_post_id, Post.status == "published")
            ).first()
            if not row:
                return None

            post, user = row
            image_url = db.execute(
                select(PostAsset.public_url).where(PostAsset.post_id == raw_post_id).order_by(PostAsset.id.asc())
            ).scalars().first()

            comment_rows = db.execute(
                select(Comment, User)
                .join(User, User.id == Comment.author_id)
                .where(Comment.post_id == raw_post_id, Comment.status == "visible")
                .order_by(Comment.id.asc())
            ).all()
            comments_preview: list[str] = []
            for comment, comment_user in comment_rows:
                author = user_service.get_public_name(comment_user)
                reply_to = str(comment.reply_to_user_name or "").strip()
                content = str(comment.content or "").replace("\n", " ").strip()
                prefix = f"{author} 回复 @{reply_to}：" if reply_to else f"{author}："
                comments_preview.append(f"{prefix}{content}"[:96])
            if len(comments_preview) > 3:
                comments_preview = comments_preview[-3:]

            liked = (
                db.execute(
                    select(PostLike).where(
                        PostLike.post_id == raw_post_id,
                        PostLike.user_id == int(user_id),
                    )
                ).scalar_one_or_none()
                is not None
            )
            saved = (
                db.execute(
                    select(PostSave).where(
                        PostSave.post_id == raw_post_id,
                        PostSave.user_id == int(user_id),
                    )
                ).scalar_one_or_none()
                is not None
            )
            knowledge_ready_map = self._load_knowledge_ready_map(db, [raw_post_id])

            return self._post_to_item(
                post=post,
                author_name=user_service.get_public_name(user),
                image_url=image_url,
                comments_preview=comments_preview,
                liked=liked,
                saved=saved,
                knowledge_ready=knowledge_ready_map.get(raw_post_id, False),
                can_delete=int(post.author_id) == int(user_id),
            )

    def toggle_like(self, post_id: str, liked: bool, user_id: int) -> dict:
        try:
            raw_id = _parse_post_id(post_id)
        except ValueError:
            return {"liked": liked, "likes": 0}

        with SessionLocal() as db:
            post = db.get(Post, raw_id)
            if not post:
                return {"liked": liked, "likes": 0}

            existing = db.execute(
                select(PostLike).where(
                    PostLike.post_id == raw_id,
                    PostLike.user_id == int(user_id),
                )
            ).scalar_one_or_none()

            if liked:
                if not existing:
                    next_id = int(db.scalar(select(func.max(PostLike.id))) or 0) + 1
                    db.add(PostLike(id=next_id, post_id=raw_id, user_id=int(user_id)))
                    post.likes_count = int(post.likes_count or 0) + 1
                    db.add(post)
                    content = _post_notification_content(post)
                    notification = db.execute(
                        select(MessageNotification).where(
                            MessageNotification.receiver_user_id == int(post.author_id),
                            MessageNotification.type == "likes",
                            MessageNotification.source_post_id == raw_id,
                            MessageNotification.source_user_id == int(user_id),
                            MessageNotification.content == content,
                        )
                    ).scalar_one_or_none()
                    if not notification:
                        next_notice_id = int(db.scalar(select(func.max(MessageNotification.id))) or 0) + 1
                        db.add(
                            MessageNotification(
                                id=next_notice_id,
                                receiver_user_id=int(post.author_id),
                                type="likes",
                                source_post_id=raw_id,
                                source_user_id=int(user_id),
                                content=content,
                                is_read=False,
                            )
                        )
            else:
                if existing:
                    db.execute(
                        delete(PostLike).where(
                            PostLike.post_id == raw_id,
                            PostLike.user_id == int(user_id),
                        )
                    )
                    post.likes_count = max(0, int(post.likes_count or 0) - 1)
                    db.add(post)
                    db.execute(
                        delete(MessageNotification).where(
                            MessageNotification.receiver_user_id == int(post.author_id),
                            MessageNotification.type == "likes",
                            MessageNotification.source_post_id == raw_id,
                            MessageNotification.source_user_id == int(user_id),
                            MessageNotification.content == _post_notification_content(post),
                        )
                    )

            db.commit()
            db.refresh(post)
            is_liked = (
                db.execute(
                    select(PostLike).where(
                        PostLike.post_id == raw_id,
                        PostLike.user_id == int(user_id),
                    )
                ).scalar_one_or_none()
                is not None
            )
            evolution_realtime_service.notify_candidate(
                post_id=raw_id,
                likes_count=int(post.likes_count or 0),
                comments_count=int(post.comments_count or 0),
                adopted=bool(post.adopted),
                reason="post_like_threshold",
            )
            return {"liked": bool(is_liked), "likes": int(post.likes_count or 0)}

    def toggle_save(self, post_id: str, saved: bool, user_id: int) -> dict:
        try:
            raw_id = _parse_post_id(post_id)
        except ValueError:
            return {"saved": saved}

        with SessionLocal() as db:
            post = db.get(Post, raw_id)
            if not post:
                return {"saved": saved}

            existing = db.execute(
                select(PostSave).where(
                    PostSave.post_id == raw_id,
                    PostSave.user_id == int(user_id),
                )
            ).scalar_one_or_none()

            if saved:
                if not existing:
                    next_id = int(db.scalar(select(func.max(PostSave.id))) or 0) + 1
                    db.add(PostSave(id=next_id, post_id=raw_id, user_id=int(user_id)))
            else:
                if existing:
                    db.execute(
                        delete(PostSave).where(
                            PostSave.post_id == raw_id,
                            PostSave.user_id == int(user_id),
                        )
                    )

            db.commit()
            is_saved = (
                db.execute(
                    select(PostSave).where(
                        PostSave.post_id == raw_id,
                        PostSave.user_id == int(user_id),
                    )
                ).scalar_one_or_none()
                is not None
            )
            return {"saved": bool(is_saved)}

    def create_post(
        self,
        category: str,
        title: str,
        content: str,
        author_id: int,
        tags: list[str] | None = None,
        image_meta: dict | None = None,
    ) -> dict:
        safe_category = str(category or "study").strip() or "study"
        safe_title = str(title or "").strip()[:120]
        safe_content = str(content or "").strip()[:2000]
        safe_tags = [str(tag).strip() for tag in (tags or []) if str(tag).strip()][:8]
        if not safe_title:
            raise ValueError("post_title_required")
        if not safe_content:
            raise ValueError("post_content_required")

        with SessionLocal() as db:
            window_start = datetime.now(tz=timezone.utc) - timedelta(minutes=30)
            recent_count = int(
                db.scalar(
                    select(func.count())
                    .select_from(Post)
                    .where(
                        Post.author_id == author_id,
                        Post.created_at >= window_start,
                        Post.status == "published",
                    )
                )
                or 0
            )
            if recent_count >= 3:
                raise ValueError("post_rate_limit_30m_3")

            next_id = int(db.scalar(select(func.max(Post.id))) or 0) + 1
            row = Post(
                id=next_id,
                author_id=author_id,
                category=safe_category,
                title=safe_title,
                content=safe_content,
                tags_json=json.dumps(safe_tags, ensure_ascii=False),
                likes_count=0,
                comments_count=0,
                adopted=False,
                status="published",
            )
            db.add(row)

            image_url = None
            if image_meta:
                next_asset_id = int(db.scalar(select(func.max(PostAsset.id))) or 0) + 1
                asset = PostAsset(
                    id=next_asset_id,
                    post_id=next_id,
                    file_name=str(image_meta.get("file_name", "")),
                    file_size=int(image_meta.get("file_size", 0)),
                    mime_type=str(image_meta.get("mime_type", "")),
                    storage_path=str(image_meta.get("storage_path", "")),
                    public_url=str(image_meta.get("public_url", "")),
                )
                db.add(asset)
                image_url = asset.public_url

            db.commit()
            db.refresh(row)
            author = db.get(User, author_id)
            author_name = user_service.get_public_name(author)
            return self._post_to_item(post=row, author_name=author_name, image_url=image_url, can_delete=True)

    def list_posts_by_author(self, user_id: int) -> list[dict]:
        with SessionLocal() as db:
            stmt = (
                select(Post, User)
                .join(User, User.id == Post.author_id)
                .where(
                    Post.status == "published",
                    Post.author_id == int(user_id),
                )
                .order_by(Post.id.desc())
            )
            rows = db.execute(stmt).all()
            post_ids = [int(row[0].id) for row in rows]

            image_map: dict[int, str] = {}
            if post_ids:
                assets = db.execute(
                    select(PostAsset).where(PostAsset.post_id.in_(post_ids)).order_by(PostAsset.id.asc())
                ).scalars().all()
                for asset in assets:
                    image_map.setdefault(int(asset.post_id), asset.public_url)

            saved_ids: set[int] = set()
            if post_ids:
                saved_rows = db.execute(
                    select(PostSave.post_id).where(
                        PostSave.post_id.in_(post_ids),
                        PostSave.user_id == int(user_id),
                    )
                ).all()
                saved_ids = {int(row[0]) for row in saved_rows}

            return [
                self._post_to_item(
                    post=row[0],
                    author_name=user_service.get_public_name(row[1]),
                    image_url=image_map.get(int(row[0].id)),
                    comments_preview=[],
                    liked=False,
                    saved=int(row[0].id) in saved_ids,
                    can_delete=True,
                )
                for row in rows
            ]

    def list_liked_posts(self, user_id: int) -> list[dict]:
        with SessionLocal() as db:
            liked_post_ids = db.execute(
                select(PostLike.post_id).where(PostLike.user_id == int(user_id)).order_by(PostLike.id.desc())
            ).scalars().all()
            if not liked_post_ids:
                return []

            rows = db.execute(
                select(Post, User)
                .join(User, User.id == Post.author_id)
                .where(Post.status == "published", Post.id.in_(liked_post_ids))
                .order_by(Post.id.desc())
            ).all()

            post_ids = [int(row[0].id) for row in rows]
            image_map: dict[int, str] = {}
            if post_ids:
                assets = db.execute(
                    select(PostAsset).where(PostAsset.post_id.in_(post_ids)).order_by(PostAsset.id.asc())
                ).scalars().all()
                for asset in assets:
                    image_map.setdefault(int(asset.post_id), asset.public_url)

            saved_ids: set[int] = set()
            if post_ids:
                saved_rows = db.execute(
                    select(PostSave.post_id).where(
                        PostSave.post_id.in_(post_ids),
                        PostSave.user_id == int(user_id),
                    )
                ).all()
                saved_ids = {int(row[0]) for row in saved_rows}

            return [
                self._post_to_item(
                    post=row[0],
                    author_name=user_service.get_public_name(row[1]),
                    image_url=image_map.get(int(row[0].id)),
                    comments_preview=[],
                    liked=True,
                    saved=int(row[0].id) in saved_ids,
                    can_delete=int(row[0].author_id) == int(user_id),
                )
                for row in rows
            ]

    def list_saved_posts(self, user_id: int) -> list[dict]:
        with SessionLocal() as db:
            saved_post_ids = db.execute(
                select(PostSave.post_id).where(PostSave.user_id == int(user_id)).order_by(PostSave.id.desc())
            ).scalars().all()
            if not saved_post_ids:
                return []

            rows = db.execute(
                select(Post, User)
                .join(User, User.id == Post.author_id)
                .where(Post.status == "published", Post.id.in_(saved_post_ids))
                .order_by(Post.id.desc())
            ).all()

            post_ids = [int(row[0].id) for row in rows]
            image_map: dict[int, str] = {}
            if post_ids:
                assets = db.execute(
                    select(PostAsset).where(PostAsset.post_id.in_(post_ids)).order_by(PostAsset.id.asc())
                ).scalars().all()
                for asset in assets:
                    image_map.setdefault(int(asset.post_id), asset.public_url)

            liked_ids: set[int] = set()
            if post_ids:
                liked_rows = db.execute(
                    select(PostLike.post_id).where(
                        PostLike.post_id.in_(post_ids),
                        PostLike.user_id == int(user_id),
                    )
                ).all()
                liked_ids = {int(row[0]) for row in liked_rows}

            return [
                self._post_to_item(
                    post=row[0],
                    author_name=user_service.get_public_name(row[1]),
                    image_url=image_map.get(int(row[0].id)),
                    comments_preview=[],
                    liked=int(row[0].id) in liked_ids,
                    saved=True,
                    can_delete=int(row[0].author_id) == int(user_id),
                )
                for row in rows
            ]

    def delete_post(self, post_id: str, user_id: int) -> dict:
        try:
            raw_post_id = _parse_post_id(post_id)
        except ValueError as exc:
            raise ValueError("post_not_found") from exc

        with SessionLocal() as db:
            post = db.get(Post, raw_post_id)
            if not post:
                raise ValueError("post_not_found")
            if int(post.author_id) != int(user_id):
                raise ValueError("post_delete_forbidden")

            comment_ids = db.execute(select(Comment.id).where(Comment.post_id == raw_post_id)).scalars().all()
            if comment_ids:
                db.execute(delete(CommentLike).where(CommentLike.comment_id.in_(comment_ids)))
                db.execute(delete(CommentAsset).where(CommentAsset.comment_id.in_(comment_ids)))
                db.execute(delete(Comment).where(Comment.id.in_(comment_ids)))

            db.execute(delete(PostAsset).where(PostAsset.post_id == raw_post_id))
            db.execute(delete(PostLike).where(PostLike.post_id == raw_post_id))
            db.execute(delete(PostSave).where(PostSave.post_id == raw_post_id))
            db.execute(delete(PostAdoption).where(PostAdoption.post_id == raw_post_id))
            db.execute(delete(MessageNotification).where(MessageNotification.source_post_id == raw_post_id))
            db.delete(post)
            db.commit()

        return {"post_id": f"p-{raw_post_id}", "deleted": True}

    def adopt_comment(
        self,
        post_id: str,
        comment_id: str,
        prune_other_comments: bool = True,
        hard_delete: bool = False,
    ) -> dict:
        try:
            raw_post_id = _parse_post_id(post_id)
            raw_comment_id = int(str(comment_id).replace("c-", ""))
        except ValueError as exc:
            raise ValueError("invalid_post_or_comment_id") from exc

        with SessionLocal() as db:
            post = db.get(Post, raw_post_id)
            if not post:
                raise ValueError("post_not_found")
            comment = db.get(Comment, raw_comment_id)
            if not comment or int(comment.post_id) != raw_post_id:
                raise ValueError("comment_not_found")

            post.adopted = True
            db.add(post)

            post_author = db.get(User, int(post.author_id))
            adopted_user = db.get(User, int(comment.author_id))
            post_author_name = user_service.get_public_name(post_author)
            adopted_user_name = user_service.get_public_name(adopted_user)

            adoption = db.execute(select(PostAdoption).where(PostAdoption.post_id == raw_post_id)).scalar_one_or_none()
            if not adoption:
                next_id = int(db.scalar(select(func.max(PostAdoption.id))) or 0) + 1
                adoption = PostAdoption(
                    id=next_id,
                    post_id=raw_post_id,
                    post_title=post.title,
                    post_author_id=int(post.author_id),
                    post_author_name=post_author_name,
                    adopted_comment_id=raw_comment_id,
                    adopted_user_id=int(comment.author_id),
                    adopted_user_name=adopted_user_name,
                    adopted_comment_text=comment.content,
                )
            else:
                adoption.post_title = post.title
                adoption.post_author_id = int(post.author_id)
                adoption.post_author_name = post_author_name
                adoption.adopted_comment_id = raw_comment_id
                adoption.adopted_user_id = int(comment.author_id)
                adoption.adopted_user_name = adopted_user_name
                adoption.adopted_comment_text = comment.content
                adoption.adopted_at = datetime.now(tz=timezone.utc)
            db.add(adoption)

            pruned_count = 0
            if prune_other_comments:
                if hard_delete:
                    others = db.execute(
                        select(Comment).where(
                            Comment.post_id == raw_post_id,
                            Comment.id != raw_comment_id,
                        )
                    ).scalars().all()
                    pruned_count = len(others)
                    other_ids = [int(row.id) for row in others]
                    if other_ids:
                        db.query(CommentAsset).filter(CommentAsset.comment_id.in_(other_ids)).delete(
                            synchronize_session=False
                        )
                    for row in others:
                        db.delete(row)
                else:
                    result = db.execute(
                        update(Comment)
                        .where(Comment.post_id == raw_post_id, Comment.id != raw_comment_id)
                        .values(status="hidden")
                    )
                    pruned_count = int(result.rowcount or 0)

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
            evolution_realtime_service.notify_candidate(
                post_id=raw_post_id,
                likes_count=int(post.likes_count or 0),
                comments_count=int(post.comments_count or 0),
                adopted=bool(post.adopted),
                reason="comment_adopted",
            )

            return {
                "post_id": f"p-{raw_post_id}",
                "comment_id": f"c-{raw_comment_id}",
                "adopted": True,
                "pruned_count": pruned_count,
                "hard_deleted": bool(hard_delete and prune_other_comments),
            }

    def list_adoptions(self) -> list[dict]:
        with SessionLocal() as db:
            rows = db.execute(select(PostAdoption).order_by(PostAdoption.adopted_at.desc(), PostAdoption.id.desc())).scalars().all()
            return [
                {
                    "post_id": f"p-{int(row.post_id)}",
                    "post_title": row.post_title,
                    "post_author_name": row.post_author_name,
                    "adopted_comment_id": f"c-{int(row.adopted_comment_id)}",
                    "adopted_user_name": row.adopted_user_name,
                    "adopted_comment_text": row.adopted_comment_text,
                    "adopted_at": row.adopted_at.isoformat() if row.adopted_at else "",
                }
                for row in rows
            ]


post_service = PostService()
