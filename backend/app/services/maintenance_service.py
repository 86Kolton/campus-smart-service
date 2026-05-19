from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select

from app.core.database import SessionLocal
from app.models.comment import Comment
from app.models.comment_asset import CommentAsset
from app.models.comment_like import CommentLike
from app.models.message import MessageNotification
from app.models.post import Post
from app.models.post_adoption import PostAdoption
from app.models.post_asset import PostAsset
from app.models.post_like import PostLike
from app.models.post_save import PostSave


class MaintenanceService:
    def reconcile_interaction_counts(self) -> dict:
        with SessionLocal() as db:
            post_like_counts = {
                int(post_id): int(count)
                for post_id, count in db.execute(
                    select(PostLike.post_id, func.count(PostLike.id)).group_by(PostLike.post_id)
                ).all()
            }
            post_comment_counts = {
                int(post_id): int(count)
                for post_id, count in db.execute(
                    select(Comment.post_id, func.count(Comment.id))
                    .where(Comment.status == "visible")
                    .group_by(Comment.post_id)
                ).all()
            }
            comment_like_counts = {
                int(comment_id): int(count)
                for comment_id, count in db.execute(
                    select(CommentLike.comment_id, func.count(CommentLike.id)).group_by(CommentLike.comment_id)
                ).all()
            }

            checked_posts = 0
            fixed_post_likes = 0
            fixed_post_comments = 0
            for post in db.execute(select(Post)).scalars().all():
                checked_posts += 1
                actual_likes = post_like_counts.get(int(post.id), 0)
                actual_comments = post_comment_counts.get(int(post.id), 0)
                post_changed = False
                if int(post.likes_count or 0) != actual_likes:
                    post.likes_count = actual_likes
                    fixed_post_likes += 1
                    post_changed = True
                if int(post.comments_count or 0) != actual_comments:
                    post.comments_count = actual_comments
                    fixed_post_comments += 1
                    post_changed = True
                if post_changed:
                    db.add(post)

            checked_comments = 0
            fixed_comment_likes = 0
            for comment in db.execute(select(Comment)).scalars().all():
                checked_comments += 1
                actual_likes = comment_like_counts.get(int(comment.id), 0)
                if int(comment.likes_count or 0) != actual_likes:
                    comment.likes_count = actual_likes
                    fixed_comment_likes += 1
                    db.add(comment)

            if fixed_post_likes or fixed_post_comments or fixed_comment_likes:
                db.commit()

            return {
                "checked_posts": checked_posts,
                "fixed_post_likes": fixed_post_likes,
                "fixed_post_comments": fixed_post_comments,
                "checked_comments": checked_comments,
                "fixed_comment_likes": fixed_comment_likes,
            }

    def cleanup_stale_unadopted_posts(self, days: int = 7) -> dict:
        safe_days = max(1, int(days or 7))
        cutoff = datetime.now(tz=timezone.utc) - timedelta(days=safe_days)

        with SessionLocal() as db:
            stale_post_ids = db.execute(
                select(Post.id).where(
                    Post.adopted.is_(False),
                    Post.created_at < cutoff,
                )
            ).scalars().all()

            if not stale_post_ids:
                return {
                    "days": safe_days,
                    "deleted_posts": 0,
                    "deleted_comments": 0,
                    "deleted_post_assets": 0,
                    "deleted_comment_assets": 0,
                }

            deleted_comments = int(
                db.scalar(select(func.count()).select_from(Comment).where(Comment.post_id.in_(stale_post_ids))) or 0
            )
            deleted_post_assets = int(
                db.scalar(select(func.count()).select_from(PostAsset).where(PostAsset.post_id.in_(stale_post_ids))) or 0
            )

            comment_ids = db.execute(
                select(Comment.id).where(Comment.post_id.in_(stale_post_ids))
            ).scalars().all()
            deleted_comment_assets = 0
            if comment_ids:
                deleted_comment_assets = int(
                    db.scalar(
                        select(func.count())
                        .select_from(CommentAsset)
                        .where(CommentAsset.comment_id.in_(comment_ids))
                    )
                    or 0
                )

            if comment_ids:
                db.execute(delete(CommentLike).where(CommentLike.comment_id.in_(comment_ids)))
                db.execute(delete(CommentAsset).where(CommentAsset.comment_id.in_(comment_ids)))
            db.execute(delete(MessageNotification).where(MessageNotification.source_post_id.in_(stale_post_ids)))
            db.execute(delete(Comment).where(Comment.post_id.in_(stale_post_ids)))
            db.execute(delete(PostAsset).where(PostAsset.post_id.in_(stale_post_ids)))
            db.execute(delete(PostLike).where(PostLike.post_id.in_(stale_post_ids)))
            db.execute(delete(PostSave).where(PostSave.post_id.in_(stale_post_ids)))
            db.execute(delete(PostAdoption).where(PostAdoption.post_id.in_(stale_post_ids)))
            db.execute(delete(Post).where(Post.id.in_(stale_post_ids)))
            db.commit()

            return {
                "days": safe_days,
                "deleted_posts": len(stale_post_ids),
                "deleted_comments": deleted_comments,
                "deleted_post_assets": deleted_post_assets,
                "deleted_comment_assets": deleted_comment_assets,
            }


maintenance_service = MaintenanceService()
