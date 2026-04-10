from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import delete, func, select

from app.core.database import SessionLocal
from app.models.post import Post
from app.models.recent_search import RecentSearchKeyword


CATEGORY_META = {
    "study": "自习教室 · 夜间",
    "canteen": "食堂 · 当日更新",
    "academic": "教务 · 临时通知",
    "market": "校园集市 · 二手交易",
}

class SearchService:
    def search_posts(self, keyword: str, sort: str) -> list[dict]:
        q = keyword.strip().lower()
        with SessionLocal() as db:
            stmt = select(Post).where(Post.status == "published").order_by(Post.id.desc())
            posts = db.execute(stmt).scalars().all()

        result: list[dict] = []
        for post in posts:
            try:
                tags = json.loads(post.tags_json or "[]")
                if not isinstance(tags, list):
                    tags = []
            except Exception:
                tags = []

            text = f"{post.title} {post.content} {' '.join([str(x) for x in tags])}".lower()
            if q and q not in text:
                continue

            result.append(
                {
                    "id": f"m-{post.id}",
                    "post_id": f"p-{post.id}",
                    "title": post.title,
                    "snippet": post.content,
                    "content": post.content,
                    "meta": CATEGORY_META.get(post.category, "社区帖子"),
                    "updated_at": "2026-04-07 00:00",
                    "hot_score": int(post.likes_count or 0) + int(post.comments_count or 0),
                    "likes": int(post.likes_count or 0),
                    "comments": int(post.comments_count or 0),
                    "keywords": [str(tag).replace("#", "") for tag in tags],
                }
            )

        if sort == "latest":
            return result
        return sorted(result, key=lambda x: x["hot_score"], reverse=True)

    def get_recent(self, user_id: int) -> list[str]:
        with SessionLocal() as db:
            rows = (
                db.execute(
                    select(RecentSearchKeyword)
                    .where(RecentSearchKeyword.user_id == int(user_id))
                    .order_by(RecentSearchKeyword.updated_at.desc(), RecentSearchKeyword.id.desc())
                    .limit(6)
                )
                .scalars()
                .all()
            )
        return [row.keyword for row in rows]

    def save_recent(self, keyword: str, user_id: int) -> None:
        if not keyword.strip():
            return
        cleaned = keyword.strip()[:128]

        with SessionLocal() as db:
            existing = db.execute(
                select(RecentSearchKeyword).where(
                    RecentSearchKeyword.user_id == int(user_id),
                    RecentSearchKeyword.keyword == cleaned,
                )
            ).scalar_one_or_none()

            if existing:
                existing.updated_at = datetime.now(tz=timezone.utc)
                db.add(existing)
            else:
                next_id = int(db.scalar(select(func.max(RecentSearchKeyword.id))) or 0) + 1
                db.add(
                    RecentSearchKeyword(
                        id=next_id,
                        user_id=int(user_id),
                        keyword=cleaned,
                    )
                )

            db.commit()

            rows = (
                db.execute(
                    select(RecentSearchKeyword)
                    .where(RecentSearchKeyword.user_id == int(user_id))
                    .order_by(RecentSearchKeyword.updated_at.desc(), RecentSearchKeyword.id.desc())
                )
                .scalars()
                .all()
            )

            for idx, row in enumerate(rows):
                if idx < 6:
                    continue
                db.delete(row)

            db.commit()

    def clear_recent(self, user_id: int) -> None:
        with SessionLocal() as db:
            db.execute(delete(RecentSearchKeyword).where(RecentSearchKeyword.user_id == int(user_id)))
            db.commit()


search_service = SearchService()
