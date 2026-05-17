from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select, update

from app.core.database import SessionLocal
from app.models.comment import Comment
from app.models.comment_like import CommentLike
from app.models.message import MessageNotification
from app.models.post import Post
from app.models.post_like import PostLike
from app.models.post_save import PostSave
from app.models.user import User
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


def _sort_value(dt: datetime | None) -> float:
    if not isinstance(dt, datetime):
        return 0
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.timestamp()


def _post_like_content(post: Post) -> str:
    title = str(post.title or "").strip() or "帖子"
    suffix = "..." if len(title) > 60 else ""
    return f"帖子赞：{title[:60]}{suffix}"


def _comment_like_content(comment: Comment) -> str:
    body = str(comment.content or "").replace("\n", " ").strip() or "图片评论"
    suffix = "..." if len(body) > 48 else ""
    return f"评论赞：{body[:48]}{suffix}"


class MessageService:
    def unread_count(self, user_id: int) -> dict:
        with SessionLocal() as db:
            safe_user_id = int(user_id)
            likes_unread = db.scalar(
                select(func.count())
                .select_from(MessageNotification)
                .join(Post, Post.id == MessageNotification.source_post_id)
                .where(
                    MessageNotification.receiver_user_id == safe_user_id,
                    MessageNotification.type == "likes",
                    MessageNotification.is_read.is_(False),
                    Post.status == "published",
                )
            )
            post_like_total = db.scalar(
                select(func.count())
                .select_from(PostLike)
                .join(Post, Post.id == PostLike.post_id)
                .where(
                    Post.author_id == safe_user_id,
                    Post.status == "published",
                )
            )
            comment_like_total = db.scalar(
                select(func.count())
                .select_from(CommentLike)
                .join(Comment, Comment.id == CommentLike.comment_id)
                .join(Post, Post.id == Comment.post_id)
                .where(
                    Comment.author_id == safe_user_id,
                    Comment.status == "visible",
                    Post.status == "published",
                )
            )
            saved_total = db.scalar(
                select(func.count())
                .select_from(PostSave)
                .join(Post, Post.id == PostSave.post_id)
                .where(PostSave.user_id == safe_user_id, Post.status == "published")
            )
        return {
            "likes_unread": int(likes_unread or 0),
            "saved_unread": 0,
            "likes_total": int(post_like_total or 0) + int(comment_like_total or 0),
            "saved_total": int(saved_total or 0),
        }

    def list_likes(self, user_id: int) -> list[dict]:
        with SessionLocal() as db:
            safe_user_id = int(user_id)
            post_rows = db.execute(
                select(PostLike, Post, User)
                .join(Post, Post.id == PostLike.post_id)
                .join(User, User.id == PostLike.user_id)
                .where(
                    Post.author_id == safe_user_id,
                    Post.status == "published",
                )
            ).all()
            comment_rows = db.execute(
                select(CommentLike, Comment, Post, User)
                .join(Comment, Comment.id == CommentLike.comment_id)
                .join(Post, Post.id == Comment.post_id)
                .join(User, User.id == CommentLike.user_id)
                .where(
                    Comment.author_id == safe_user_id,
                    Comment.status == "visible",
                    Post.status == "published",
                )
            ).all()

        items: list[dict] = []
        for row, post, user in post_rows:
            actor = user_service.get_public_name(user)
            items.append(
                {
                    "id": f"pl-{row.id}",
                    "main": f"@{actor} 赞了你：{_post_like_content(post)}",
                    "meta": f"{_format_relative(row.created_at)} · 来自帖子互动",
                    "post_id": f"p-{post.id}",
                    "source_type": "feed",
                    "saved": False,
                    "_sort_at": _sort_value(row.created_at),
                }
            )
        for row, comment, post, user in comment_rows:
            actor = user_service.get_public_name(user)
            items.append(
                {
                    "id": f"cl-{row.id}",
                    "main": f"@{actor} 赞了你：{_comment_like_content(comment)}",
                    "meta": f"{_format_relative(row.created_at)} · 来自评论互动",
                    "post_id": f"p-{post.id}",
                    "source_type": "feed",
                    "saved": False,
                    "_sort_at": _sort_value(row.created_at),
                }
            )

        items.sort(key=lambda item: (float(item.get("_sort_at") or 0), str(item.get("id") or "")), reverse=True)
        for item in items:
            item.pop("_sort_at", None)
        return items

    def list_saved(self, user_id: int) -> list[dict]:
        with SessionLocal() as db:
            rows = db.execute(
                select(PostSave, Post, User)
                .join(Post, Post.id == PostSave.post_id)
                .join(User, User.id == Post.author_id)
                .where(PostSave.user_id == int(user_id), Post.status == "published")
                .order_by(PostSave.id.desc())
            ).all()

        items: list[dict] = []
        for row, post, user in rows:
            author = user_service.get_public_name(user)
            title = str(post.title or "").strip() or "校园帖子"
            items.append(
                {
                    "id": f"s-{row.id}",
                    "main": title,
                    "meta": f"作者 @{author} · {_format_relative(row.created_at)} · 已收藏",
                    "post_id": f"p-{post.id}",
                    "source_type": "feed",
                    "saved": True,
                }
            )
        return items

    def mark_read(self, msg_type: str, user_id: int) -> None:
        if msg_type == "saved":
            return
        with SessionLocal() as db:
            stmt = update(MessageNotification).where(MessageNotification.receiver_user_id == int(user_id))
            if msg_type == "likes":
                stmt = stmt.where(MessageNotification.type == "likes")
            stmt = stmt.values(is_read=True)
            db.execute(stmt)
            db.commit()


message_service = MessageService()
