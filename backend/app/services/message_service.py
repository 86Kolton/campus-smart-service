from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select, update

from app.core.database import SessionLocal
from app.models.message import MessageNotification
from app.models.post import Post
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


class MessageService:
    def unread_count(self, user_id: int) -> dict:
        with SessionLocal() as db:
            likes_unread = db.scalar(
                select(func.count())
                .select_from(MessageNotification)
                .where(
                    MessageNotification.receiver_user_id == int(user_id),
                    MessageNotification.type == "likes",
                    MessageNotification.is_read.is_(False),
                )
            )
            likes_total = db.scalar(
                select(func.count())
                .select_from(MessageNotification)
                .where(
                    MessageNotification.receiver_user_id == int(user_id),
                    MessageNotification.type == "likes",
                )
            )
            saved_total = db.scalar(
                select(func.count())
                .select_from(PostSave)
                .where(PostSave.user_id == int(user_id))
            )
        return {
            "likes_unread": int(likes_unread or 0),
            "saved_unread": 0,
            "likes_total": int(likes_total or 0),
            "saved_total": int(saved_total or 0),
        }

    def list_likes(self, user_id: int) -> list[dict]:
        with SessionLocal() as db:
            rows = db.execute(
                select(MessageNotification, User)
                .join(User, User.id == MessageNotification.source_user_id)
                .where(
                    MessageNotification.receiver_user_id == int(user_id),
                    MessageNotification.type == "likes",
                )
                .order_by(MessageNotification.id.desc())
            ).all()

        items: list[dict] = []
        for row, user in rows:
            actor = user_service.get_public_name(user)
            items.append(
                {
                    "id": f"l-{row.id}",
                    "main": f"@{actor} 赞了你：{row.content}",
                    "meta": f"{_format_relative(row.created_at)} · 来自帖子或评论互动",
                    "post_id": f"p-{row.source_post_id}",
                    "source_type": "feed",
                    "saved": False,
                }
            )
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
