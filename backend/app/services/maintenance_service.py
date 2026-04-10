from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select

from app.core.database import SessionLocal
from app.models.comment import Comment
from app.models.comment_asset import CommentAsset
from app.models.post import Post
from app.models.post_adoption import PostAdoption
from app.models.post_asset import PostAsset


class MaintenanceService:
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

            db.execute(delete(CommentAsset).where(CommentAsset.comment_id.in_(comment_ids)))
            db.execute(delete(Comment).where(Comment.post_id.in_(stale_post_ids)))
            db.execute(delete(PostAsset).where(PostAsset.post_id.in_(stale_post_ids)))
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
