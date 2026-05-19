from __future__ import annotations

import json
import re
import unicodedata
from datetime import datetime, timezone

from sqlalchemy import delete, func, select

from app.core.database import SessionLocal
from app.models.post import Post
from app.models.recent_search import RecentSearchKeyword
from app.models.user import User
from app.services.post_service import is_public_feed_artifact
from app.services.user_service import user_service


CATEGORY_META = {
    "study": "自习教室 · 夜间",
    "canteen": "食堂 · 当日更新",
    "academic": "教务 · 临时通知",
    "market": "校园集市 · 二手交易",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+|[\u4e00-\u9fff]+")
_COMPACT_RE = re.compile(r"[^a-z0-9\u4e00-\u9fff]+")
_CAMPUS_QUERY_TERMS = (
    "河北大学",
    "图书馆",
    "成绩单",
    "统一认证",
    "教务处",
    "教务",
    "学生事务",
    "办事大厅",
    "电子资源",
    "校外访问",
    "五四路",
    "七一路",
    "裕华路",
    "校区",
    "自习",
    "空教室",
    "食堂",
    "宿舍",
    "跑腿",
    "课程评价",
    "跨校",
    "组队",
    "选课",
    "考试",
    "邮编",
    "心理",
    "学生邮箱",
    "企业微信",
    "校园卡",
    "缴费",
    "财务",
    "论文",
    "文献",
    "毕设",
    "webvpn",
    "hbu",
)


def _normalize(value: object) -> str:
    return unicodedata.normalize("NFKC", str(value or "")).casefold()


def _compact(value: object) -> str:
    return _COMPACT_RE.sub("", _normalize(value))


def _format_updated_at(value: datetime | None) -> str:
    if not isinstance(value, datetime):
        return ""
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone().strftime("%Y-%m-%d %H:%M")


def _query_terms(keyword: str) -> tuple[str, list[str]]:
    normalized = _normalize(keyword).strip()
    compact_query = _compact(normalized)
    candidates: list[str] = []
    for part in normalized.split():
        candidates.extend(_TOKEN_RE.findall(part))
    if not candidates and compact_query:
        candidates.extend(_TOKEN_RE.findall(compact_query))
    for term in _CAMPUS_QUERY_TERMS:
        normalized_term = _normalize(term)
        if normalized_term and normalized_term in compact_query:
            candidates.append(normalized_term)

    terms: list[str] = []
    seen: set[str] = set()
    for item in candidates:
        term = _compact(item)
        if not term or term in seen:
            continue
        seen.add(term)
        terms.append(term)
    return compact_query, terms


class SearchService:
    def search_posts(self, keyword: str, sort: str) -> list[dict]:
        q, terms = _query_terms(keyword)
        with SessionLocal() as db:
            stmt = (
                select(Post, User)
                .join(User, User.id == Post.author_id)
                .where(Post.status == "published")
                .order_by(Post.created_at.desc(), Post.id.desc())
            )
            posts = db.execute(stmt).all()

        strict_matches: list[tuple[int, dict]] = []
        loose_matches: list[tuple[int, dict]] = []
        for post, user in posts:
            if is_public_feed_artifact(post, author_username=user.username, author_name=user_service.get_public_name(user)):
                continue
            try:
                tags = json.loads(post.tags_json or "[]")
                if not isinstance(tags, list):
                    tags = []
            except Exception:
                tags = []

            title_keywords = f"{post.title} {' '.join([str(x) for x in tags])}"
            text = f"{title_keywords} {post.content}"
            compact_title_keywords = _compact(title_keywords)
            compact_text = _compact(text)
            if q and not terms and q not in compact_text:
                continue

            score = 0
            matched_terms = 0
            if q and q in compact_text:
                score += 10
            for term in terms:
                if term in compact_title_keywords:
                    score += 6
                    matched_terms += 1
                elif term in compact_text:
                    score += 3
                    matched_terms += 1

            if q and terms and score <= 0:
                continue

            hot_score = int(post.likes_count or 0) + int(post.comments_count or 0)
            item = {
                "id": f"m-{post.id}",
                "post_id": f"p-{post.id}",
                "title": post.title,
                "snippet": post.content,
                "content": post.content,
                "meta": CATEGORY_META.get(post.category, "社区帖子"),
                "updated_at": _format_updated_at(post.created_at),
                "hot_score": hot_score,
                "likes": int(post.likes_count or 0),
                "comments": int(post.comments_count or 0),
                "keywords": [str(tag).replace("#", "") for tag in tags],
            }
            bucket = (
                strict_matches
                if not terms or matched_terms == len(terms) or (q and q in compact_text)
                else loose_matches
            )
            bucket.append((score, item))

        if sort == "latest":
            matches = strict_matches if strict_matches else loose_matches
            return [item for _, item in matches]

        matches = strict_matches if strict_matches else loose_matches
        return [
            item
            for _, item in sorted(
                matches,
                key=lambda row: (row[0], row[1]["hot_score"]),
                reverse=True,
            )
        ]

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
