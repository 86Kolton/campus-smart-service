from __future__ import annotations

from difflib import SequenceMatcher
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import func, or_, select

from app.core.database import SessionLocal
from app.models.comment import Comment
from app.models.evolution_review import EvolutionReview
from app.models.knowledge import KnowledgeDocument
from app.models.post import Post
from app.models.post_adoption import PostAdoption
from app.models.user import User
from app.services.ingest_service import ingest_service
from app.services.kb_service import kb_service
from app.services.knowledge_cache_service import knowledge_cache_service
from app.services.qdrant_service import qdrant_service
from app.services.evolution_review_service import evolution_review_service
from app.services.user_service import user_service


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _safe_iso(value: datetime | None) -> str:
    if value is None:
        return _utcnow().isoformat()
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.isoformat()


class EvolutionService:
    _NON_WORD_RE = re.compile(r"[^0-9a-z\u4e00-\u9fff]+", re.I)
    _CATEGORY_PRIORITY_BONUS = {
        "academic": 18,
        "study": 16,
        "canteen": 16,
        "market": 10,
    }
    _DETAIL_HINTS = (
        "今天",
        "明天",
        "今晚",
        "上午",
        "中午",
        "下午",
        "晚上",
        "食堂",
        "图书馆",
        "校区",
        "主楼",
        "宿舍",
        "窗口",
        "办理",
        "打印",
        "选课",
        "课表",
        "自习",
        "排队",
        "分钟",
        "点",
    )

    def __init__(self) -> None:
        self._data_root = Path(__file__).resolve().parents[2] / "data" / "evolution"

    def _parse_tags(self, tags_json: str | None) -> list[str]:
        try:
            parsed = json.loads(tags_json or "[]")
            if isinstance(parsed, list):
                return [str(item).strip() for item in parsed if str(item).strip()]
        except Exception:
            pass
        return []

    def _doc_name(self, post_id: int) -> str:
        return f"evo-post-{post_id}.md"

    def _doc_path(self, kb_id: int, post_id: int) -> Path:
        target = self._data_root / f"kb_{kb_id}"
        target.mkdir(parents=True, exist_ok=True)
        return target / self._doc_name(post_id)

    def _build_markdown(
        self,
        post: Post,
        author_name: str,
        tags: list[str],
        top_comments: list[dict],
        adopted_comment: str,
        review: dict,
    ) -> str:
        lines = [
            f"# 校园论坛录用：{post.title}",
            "",
            f"- 帖子编号：p-{int(post.id)}",
            f"- 分类：{post.category}",
            f"- 发布者：{author_name}",
            f"- 热度：点赞 {int(post.likes_count or 0)} · 评论 {int(post.comments_count or 0)}",
            f"- 入库时间：{_safe_iso(_utcnow())}",
            f"- 原帖跳转：https://rag-user.yyaxx.cc/#post=p-{int(post.id)}",
            "",
            "## AI 筛选结论",
            str(review.get("clean_summary") or "").strip() or "内容质量达标，已进入校园知识库。",
            "",
            f"审核说明：{str(review.get('reason') or '').strip()}",
            "",
            "## 原帖正文",
            str(post.content or "").strip(),
            "",
        ]
        if tags:
            lines.extend(["## 标签", " ".join(tags), ""])
        if adopted_comment:
            lines.extend(["## 录用评论", adopted_comment, ""])
        if top_comments:
            lines.append("## 讨论补充")
            for item in top_comments[:4]:
                author = str(item.get("author") or "社区用户").strip()
                content = str(item.get("content") or "").strip()
                if not content:
                    continue
                lines.append(f"- {author}：{content}")
            lines.append("")
        return "\n".join(lines).strip() + "\n"

    def _normalize_signature(self, text: str) -> str:
        lowered = str(text or "").lower()
        compact = self._NON_WORD_RE.sub(" ", lowered)
        return " ".join(compact.split())

    def _candidate_signature(self, post: Post, tags: list[str], adopted_comment: str, top_comments: list[dict]) -> str:
        parts = [
            str(post.title or ""),
            str(post.content or ""),
            " ".join(tags[:6]),
            str(adopted_comment or ""),
        ]
        for item in top_comments[:3]:
            parts.append(str(item.get("content") or ""))
        return self._normalize_signature(" ".join(parts))

    def _signature_hash(self, signature: str) -> str:
        return hashlib.sha256(str(signature or "").encode("utf-8")).hexdigest()

    def _candidate_priority(
        self,
        post: Post,
        tags: list[str],
        top_comments: list[dict],
        adopted_comment: str,
    ) -> tuple[int, list[dict[str, object]]]:
        score = 0
        breakdown: list[dict[str, object]] = []
        likes = int(post.likes_count or 0)
        comments = int(post.comments_count or 0)
        content = str(post.content or "").strip()

        like_bonus = min(48, likes)
        if like_bonus:
            score += like_bonus
            breakdown.append({"label": "likes_signal", "delta": like_bonus})

        comment_bonus = min(45, comments * 9)
        if comment_bonus:
            score += comment_bonus
            breakdown.append({"label": "comments_signal", "delta": comment_bonus})

        if bool(post.adopted):
            score += 42
            breakdown.append({"label": "forum_adoption_bonus", "delta": 42})

        category_bonus = int(self._CATEGORY_PRIORITY_BONUS.get(str(post.category or "").strip(), 0))
        if category_bonus:
            score += category_bonus
            breakdown.append({"label": "category_bonus", "delta": category_bonus})

        if len(str(post.title or "").strip()) >= 10:
            score += 12
            breakdown.append({"label": "title_clarity_bonus", "delta": 12})

        if len(content) >= 40:
            score += 14
            breakdown.append({"label": "content_density_bonus", "delta": 14})
        if len(content) >= 90:
            score += 8
            breakdown.append({"label": "content_detail_bonus", "delta": 8})

        if tags:
            tag_bonus = min(12, len(tags) * 3)
            score += tag_bonus
            breakdown.append({"label": "tag_bonus", "delta": tag_bonus})

        useful_comments = sum(1 for item in top_comments[:4] if len(str(item.get("content") or "").strip()) >= 12)
        if useful_comments:
            discussion_bonus = min(16, useful_comments * 4)
            score += discussion_bonus
            breakdown.append({"label": "discussion_bonus", "delta": discussion_bonus})

        if adopted_comment:
            score += 10
            breakdown.append({"label": "adopted_comment_bonus", "delta": 10})

        haystack = " ".join(
            [
                str(post.title or ""),
                content,
                " ".join(tags),
                str(adopted_comment or ""),
                " ".join(str(item.get("content") or "") for item in top_comments[:4]),
            ]
        )
        detail_hits = sum(1 for hint in self._DETAIL_HINTS if hint in haystack)
        if detail_hits:
            detail_bonus = min(18, detail_hits * 2)
            score += detail_bonus
            breakdown.append({"label": "detail_hint_bonus", "delta": detail_bonus, "hits": detail_hits})

        created_at = getattr(post, "created_at", None)
        if created_at is not None:
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            age_days = max(0.0, (_utcnow() - created_at).total_seconds() / 86400.0)
            age_bonus = min(18, int(age_days) * 3)
            if age_bonus:
                score += age_bonus
                breakdown.append({"label": "pending_backlog_bonus", "delta": age_bonus, "age_days": round(age_days, 1)})

        return score, breakdown

    def _load_existing_signatures(self, kb_id: int) -> list[dict]:
        with SessionLocal() as db:
            docs = (
                db.execute(
                    select(KnowledgeDocument).where(
                        KnowledgeDocument.kb_id == int(kb_id),
                        KnowledgeDocument.file_name.like("evo-post-%"),
                    )
                )
                .scalars()
                .all()
            )
            reviews = (
                db.execute(
                    select(EvolutionReview).where(EvolutionReview.kb_id == int(kb_id)).order_by(EvolutionReview.id.desc())
                )
                .scalars()
                .all()
            )
        items: list[dict] = []
        for row in docs:
            text = ""
            storage_path = Path(str(row.storage_path or "").strip())
            if storage_path.exists() and storage_path.is_file():
                try:
                    text = storage_path.read_text(encoding="utf-8")
                except Exception:
                    text = ""
            items.append(
                {
                    "post_id": int(str(row.file_name).replace("evo-post-", "").replace(".md", "") or 0),
                    "title": str(row.file_name or ""),
                    "signature": self._normalize_signature(text),
                    "signature_hash": "",
                }
            )
        for row in reviews:
            try:
                detail = json.loads(str(row.detail_json or "{}"))
            except Exception:
                detail = {}
            signature_hash = str(detail.get("signature_hash") or "").strip()
            if not signature_hash:
                continue
            items.append(
                {
                    "post_id": int(row.post_id or 0),
                    "title": str(row.post_title or ""),
                    "signature": "",
                    "signature_hash": signature_hash,
                }
            )
        return items

    def _load_reviewed_post_ids(self, kb_id: int) -> set[int]:
        with SessionLocal() as db:
            rows = db.execute(select(EvolutionReview.post_id).where(EvolutionReview.kb_id == int(kb_id))).all()
        return {int(row[0]) for row in rows if row and row[0] is not None}

    def _match_duplicate(
        self,
        post_id: int,
        title: str,
        signature: str,
        signature_hash: str,
        references: list[dict],
    ) -> dict | None:
        if not signature:
            return None
        normalized_title = self._normalize_signature(title)
        for item in references:
            if int(item.get("post_id") or 0) == int(post_id):
                continue
            reference_hash = str(item.get("signature_hash") or "").strip()
            if signature_hash and reference_hash and signature_hash == reference_hash:
                return {"post_id": int(item.get("post_id") or 0), "score": 1.0, "method": "hash"}
            reference_signature = str(item.get("signature") or "").strip()
            if not reference_signature:
                continue
            similarity = SequenceMatcher(None, signature[:1200], reference_signature[:1200]).ratio()
            if similarity >= 0.9:
                return {"post_id": int(item.get("post_id") or 0), "score": similarity, "method": "similarity"}
            if normalized_title and normalized_title in reference_signature and similarity >= 0.78:
                return {"post_id": int(item.get("post_id") or 0), "score": similarity, "method": "similarity"}
        return None

    def _collect_candidates(
        self,
        kb_id: int,
        min_likes: int,
        min_comments: int,
        limit: int | None = None,
        include_reviewed: bool = False,
    ) -> dict[str, object]:
        reviewed_post_ids = set() if include_reviewed else self._load_reviewed_post_ids(int(kb_id))
        with SessionLocal() as db:
            rows = (
                db.execute(
                    select(Post, User)
                    .join(User, User.id == Post.author_id)
                    .where(
                        Post.status == "published",
                        or_(
                            Post.adopted.is_(True),
                            Post.likes_count >= int(min_likes),
                            Post.comments_count >= int(min_comments),
                        ),
                    )
                    .order_by(Post.id.desc())
                )
                .all()
            )
            if not rows:
                return {
                    "items": [],
                    "eligible_total": 0,
                    "pending_total": 0,
                    "reviewed_skipped": 0,
                }

            post_ids = [int(post.id) for post, _ in rows]
            adoption_rows = (
                db.execute(
                    select(PostAdoption).where(PostAdoption.post_id.in_(post_ids)).order_by(PostAdoption.adopted_at.desc())
                )
                .scalars()
                .all()
            )
            adoption_map: dict[int, PostAdoption] = {}
            for adoption in adoption_rows:
                adoption_map.setdefault(int(adoption.post_id), adoption)

            comment_rows = (
                db.execute(
                    select(Comment, User)
                    .join(User, User.id == Comment.author_id)
                    .where(Comment.post_id.in_(post_ids), Comment.status == "visible")
                    .order_by(Comment.likes_count.desc(), Comment.id.asc())
                )
                .all()
            )
            comment_map: dict[int, list[dict]] = {}
            for comment, comment_user in comment_rows:
                comment_map.setdefault(int(comment.post_id), []).append(
                    {
                        "id": int(comment.id),
                        "author": user_service.get_public_name(comment_user),
                        "content": str(comment.content or "").strip(),
                        "likes": int(comment.likes_count or 0),
                    }
                )

            pending_rows: list[tuple[Post, User]] = []
            reviewed_skipped = 0
            for post, author in rows:
                if reviewed_post_ids and int(post.id) in reviewed_post_ids:
                    reviewed_skipped += 1
                    continue
                pending_rows.append((post, author))

            pending_total = len(pending_rows)
            prioritized_rows: list[dict[str, object]] = []
            for post, author in pending_rows:
                adoption = adoption_map.get(int(post.id))
                tags = self._parse_tags(post.tags_json)
                top_comments = comment_map.get(int(post.id), [])[:4]
                adopted_comment = str(adoption.adopted_comment_text or "").strip() if adoption else ""
                priority_score, priority_breakdown = self._candidate_priority(
                    post=post,
                    tags=tags,
                    top_comments=top_comments,
                    adopted_comment=adopted_comment,
                )
                prioritized_rows.append(
                    {
                        "kb_id": int(kb_id),
                        "post": post,
                        "author_name": user_service.get_public_name(author),
                        "tags": tags,
                        "top_comments": top_comments,
                        "adopted_comment": adopted_comment,
                        "candidate_priority": priority_score,
                        "candidate_priority_breakdown": priority_breakdown,
                    }
                )

            prioritized_rows.sort(
                key=lambda item: (
                    int(item["candidate_priority"]),
                    int(getattr(item["post"], "id", 0)),
                ),
                reverse=True,
            )
            if limit:
                prioritized_rows = prioritized_rows[: int(limit)]
            return {
                "items": prioritized_rows,
                "eligible_total": len(rows),
                "pending_total": pending_total,
                "reviewed_skipped": reviewed_skipped,
            }

    def _find_document(self, kb_id: int, post_id: int) -> dict | None:
        file_name = self._doc_name(post_id)
        with SessionLocal() as db:
            row = db.execute(
                select(KnowledgeDocument).where(
                    KnowledgeDocument.kb_id == int(kb_id),
                    KnowledgeDocument.file_name == file_name,
                )
            ).scalar_one_or_none()
            if not row:
                return None
            return {
                "id": int(row.id),
                "chunk_count": int(row.chunk_count or 0),
                "storage_path": str(row.storage_path or ""),
            }

    def _remove_document(self, kb_id: int, post_id: int) -> None:
        file_name = self._doc_name(post_id)
        with SessionLocal() as db:
            row = db.execute(
                select(KnowledgeDocument).where(
                    KnowledgeDocument.kb_id == int(kb_id),
                    KnowledgeDocument.file_name == file_name,
                )
            ).scalar_one_or_none()
            if not row:
                return
            document_id = int(row.id)
            chunk_count = int(row.chunk_count or 0)
            storage_path = str(row.storage_path or "")
            db.delete(row)
            db.commit()
        qdrant_service.delete_document_chunks(kb_id=int(kb_id), document_id=document_id)
        if storage_path:
            Path(storage_path).unlink(missing_ok=True)
        kb_service.bump_stats(int(kb_id), docs_delta=-1, chunks_delta=-chunk_count)

    def _upsert_document(self, kb_id: int, post: Post, markdown: str) -> tuple[int, int]:
        file_name = self._doc_name(int(post.id))
        storage_path = self._doc_path(int(kb_id), int(post.id))
        storage_path.write_text(markdown, encoding="utf-8")

        created = False
        with SessionLocal() as db:
            row = db.execute(
                select(KnowledgeDocument).where(
                    KnowledgeDocument.kb_id == int(kb_id),
                    KnowledgeDocument.file_name == file_name,
                )
            ).scalar_one_or_none()
            if row is None:
                next_id = int(db.scalar(select(func.max(KnowledgeDocument.id))) or 0) + 1
                row = KnowledgeDocument(
                    id=next_id,
                    kb_id=int(kb_id),
                    file_name=file_name,
                    file_ext="md",
                    file_size=0,
                    storage_path=str(storage_path),
                    mime_type="text/markdown",
                    status="uploaded",
                    chunk_count=0,
                    error_message="",
                    uploaded_by=1,
                )
                created = True

            row.file_ext = "md"
            row.file_size = len(markdown.encode("utf-8"))
            row.storage_path = str(storage_path)
            row.mime_type = "text/markdown"
            row.status = "uploaded"
            row.error_message = ""
            db.add(row)
            db.commit()
            db.refresh(row)
            document_id = int(row.id)

        if created:
            kb_service.bump_stats(int(kb_id), docs_delta=1)

        qdrant_service.delete_document_chunks(kb_id=int(kb_id), document_id=document_id)
        chunk_count = int(ingest_service.ingest_document(int(kb_id), document_id, "md", markdown.encode("utf-8")) or 0)
        return document_id, chunk_count

    def _write_review(self, kb_id: int, post: Post, review: dict, document_id: int | None) -> None:
        with SessionLocal() as db:
            next_id = int(db.scalar(select(func.max(EvolutionReview.id))) or 0) + 1
            db.add(
                EvolutionReview(
                    id=next_id,
                    kb_id=int(kb_id),
                    post_id=int(post.id),
                    post_title=str(post.title or ""),
                    decision=str(review.get("decision") or "reject"),
                    overall_score=int(review.get("overall_score") or 0),
                    reviewer_model=str(review.get("reviewer_model") or ""),
                    reason=str(review.get("reason") or ""),
                    detail_json=json.dumps(review.get("raw") or {}, ensure_ascii=False),
                    document_id=document_id,
                )
            )
            db.commit()

    def sync_high_quality_posts(
        self,
        kb_id: int = 1,
        min_likes: int = 30,
        min_comments: int = 5,
        limit: int | None = None,
        include_reviewed: bool = False,
    ) -> dict:
        safe_limit = max(1, int(limit)) if limit else None
        candidate_bundle = self._collect_candidates(
            kb_id=kb_id,
            min_likes=min_likes,
            min_comments=min_comments,
            limit=safe_limit,
            include_reviewed=include_reviewed,
        )
        candidates = list(candidate_bundle["items"])
        pending_total = int(candidate_bundle["pending_total"] or 0)
        reviewed_skipped = int(candidate_bundle["reviewed_skipped"] or 0)
        if not candidates:
            return {
                "synced_posts": 0,
                "skipped_posts": reviewed_skipped,
                "accepted_posts": 0,
                "rejected_posts": 0,
                "indexed_documents": 0,
                "kb_id": int(kb_id),
                "limit": safe_limit,
                "pending_posts": pending_total,
                "remaining_posts": 0,
                "reviewed_posts_skipped": reviewed_skipped,
            }

        accepted_posts = 0
        rejected_posts = 0
        indexed_documents = 0
        signature_refs = self._load_existing_signatures(int(kb_id))

        for item in candidates:
            post = item["post"]
            signature = self._candidate_signature(
                post=post,
                tags=list(item["tags"]),
                adopted_comment=str(item["adopted_comment"] or ""),
                top_comments=list(item["top_comments"]),
            )
            signature_hash = self._signature_hash(signature)
            duplicate_hit = self._match_duplicate(
                post_id=int(post.id),
                title=str(post.title or ""),
                signature=signature,
                signature_hash=signature_hash,
                references=signature_refs,
            )
            review_input = {
                "title": str(post.title or ""),
                "content": str(post.content or ""),
                "category": str(post.category or ""),
                "tags": list(item["tags"]),
                "likes_count": int(post.likes_count or 0),
                "comments_count": int(post.comments_count or 0),
                "adopted": bool(post.adopted),
                "adopted_comment": str(item["adopted_comment"] or ""),
                "top_comments": list(item["top_comments"]),
            }
            if duplicate_hit:
                review = {
                    "decision": "reject",
                    "overall_score": 18,
                    "reviewer_model": "duplicate-guard",
                    "reason": f"与已审核过的论坛内容高度重复，重复来源 p-{duplicate_hit['post_id']}，已拦截反复入库。",
                    "clean_summary": str(post.content or "").strip()[:96],
                    "raw": {
                        "duplicate_post_id": f"p-{duplicate_hit['post_id']}",
                        "similarity": duplicate_hit["score"],
                        "duplicate_method": duplicate_hit.get("method", "similarity"),
                    },
                }
            else:
                review = evolution_review_service.review_post(review_input)
            review_raw = dict(review.get("raw") or {})
            review_raw["signature_hash"] = signature_hash
            review_raw["candidate_priority"] = int(item.get("candidate_priority") or 0)
            review_raw["candidate_priority_breakdown"] = list(item.get("candidate_priority_breakdown") or [])
            review["raw"] = review_raw
            document_id: int | None = None
            if str(review.get("decision") or "") == "pass":
                markdown = self._build_markdown(
                    post=post,
                    author_name=str(item["author_name"] or "社区用户"),
                    tags=list(item["tags"]),
                    top_comments=list(item["top_comments"]),
                    adopted_comment=str(item["adopted_comment"] or ""),
                    review=review,
                )
                document_id, _ = self._upsert_document(int(kb_id), post, markdown)
                signature_refs.append(
                    {
                        "post_id": int(post.id),
                        "title": str(post.title or ""),
                        "signature": signature,
                        "signature_hash": signature_hash,
                    }
                )
                accepted_posts += 1
                indexed_documents += 1
            else:
                self._remove_document(int(kb_id), int(post.id))
                rejected_posts += 1

            self._write_review(int(kb_id), post, review, document_id=document_id)

        knowledge_cache_service.rebuild_chunks()
        return {
            "synced_posts": len(candidates),
            "skipped_posts": reviewed_skipped,
            "accepted_posts": accepted_posts,
            "rejected_posts": rejected_posts,
            "indexed_documents": indexed_documents,
            "kb_id": int(kb_id),
            "limit": safe_limit,
            "pending_posts": pending_total,
            "remaining_posts": max(0, pending_total - len(candidates)),
            "reviewed_posts_skipped": reviewed_skipped,
        }

    def list_reviews(self, limit: int = 50) -> list[dict]:
        with SessionLocal() as db:
            rows = (
                db.execute(select(EvolutionReview).order_by(EvolutionReview.id.desc()).limit(max(1, int(limit))))
                .scalars()
                .all()
            )
        items: list[dict] = []
        for row in rows:
            try:
                detail = json.loads(str(row.detail_json or "{}"))
            except Exception:
                detail = {}
            items.append(
                {
                    "id": int(row.id),
                    "kb_id": int(row.kb_id),
                    "post_id": f"p-{int(row.post_id)}",
                    "post_title": str(row.post_title or ""),
                    "decision": str(row.decision or "reject"),
                    "overall_score": int(row.overall_score or 0),
                    "reviewer_model": str(row.reviewer_model or ""),
                    "reason": str(row.reason or ""),
                    "document_id": int(row.document_id) if row.document_id else None,
                    "created_at": _safe_iso(row.created_at),
                    "detail": detail if isinstance(detail, dict) else {},
                }
            )
        return items


evolution_service = EvolutionService()
