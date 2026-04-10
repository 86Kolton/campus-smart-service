from __future__ import annotations

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.errand_task import ErrandTask
from app.models.message import MessageNotification
from app.models.post import Post
from app.models.user import User
from app.services.user_service import user_service


class ProfileService:
    def summary(self, user_id: int) -> dict:
        with SessionLocal() as db:
            safe_user_id = int(user_id)
            user = db.get(User, safe_user_id)
            post_count = (
                db.scalar(
                    select(func.count()).select_from(Post).where(Post.author_id == safe_user_id, Post.status == "published")
                )
                or 0
            )
            errand_count = (
                db.scalar(select(func.count()).select_from(ErrandTask).where(ErrandTask.publisher_id == safe_user_id))
                or 0
            )
            like_count = (
                db.scalar(
                    select(func.count()).select_from(MessageNotification).where(
                        MessageNotification.receiver_user_id == safe_user_id,
                        MessageNotification.type == "likes",
                    )
                )
                or 0
            )
            likes_unread = (
                db.scalar(
                    select(func.count()).select_from(MessageNotification).where(
                        MessageNotification.receiver_user_id == safe_user_id,
                        MessageNotification.type == "likes",
                        MessageNotification.is_read.is_(False),
                    )
                )
                or 0
            )

        name = user_service.get_visible_profile_name(user) if user else "赵同学"
        public_name = user_service.get_public_name(user)
        wechat_bound = bool(user and user.wechat_openid)
        bind_state = "已绑定微信身份" if wechat_bound else "未绑定微信身份"
        return {
            "name": name,
            "public_name": public_name,
            "meta": "河北大学 · 软件工程 2022 级",
            "bind_state": bind_state,
            "wechat_bound": wechat_bound,
            "posts": int(post_count) + int(errand_count),
            "likes": int(like_count),
            "feed_posts": int(post_count),
            "errand_posts": int(errand_count),
            "likes_unread": int(likes_unread),
        }


profile_service = ProfileService()
