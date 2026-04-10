from __future__ import annotations

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.knowledge import KnowledgeBase


CURRENT_ADMIN_ID = 1


class KnowledgeBaseService:
    def list_kb(self) -> list[dict]:
        with SessionLocal() as db:
            stmt = select(KnowledgeBase).order_by(KnowledgeBase.id.asc())
            rows = db.execute(stmt).scalars().all()
        return [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "status": row.status,
                "doc_count": int(row.doc_count or 0),
                "chunk_count": int(row.chunk_count or 0),
            }
            for row in rows
        ]

    def create_kb(self, name: str, description: str) -> dict:
        with SessionLocal() as db:
            next_id = int(db.scalar(select(func.max(KnowledgeBase.id))) or 0) + 1
            row = KnowledgeBase(
                id=next_id,
                name=name,
                description=description,
                status="active",
                visibility="private",
                doc_count=0,
                chunk_count=0,
                created_by=CURRENT_ADMIN_ID,
            )
            db.add(row)
            db.commit()
            db.refresh(row)
        return {
            "id": row.id,
            "name": row.name,
            "description": row.description,
            "status": row.status,
            "doc_count": int(row.doc_count or 0),
            "chunk_count": int(row.chunk_count or 0),
        }

    def exists(self, kb_id: int) -> bool:
        with SessionLocal() as db:
            return db.get(KnowledgeBase, int(kb_id)) is not None

    def delete_kb(self, kb_id: int) -> bool:
        with SessionLocal() as db:
            row = db.get(KnowledgeBase, kb_id)
            if not row:
                return False
            db.delete(row)
            db.commit()
            return True

    def bump_stats(self, kb_id: int, docs_delta: int = 0, chunks_delta: int = 0) -> None:
        with SessionLocal() as db:
            kb = db.get(KnowledgeBase, kb_id)
            if not kb:
                return
            kb.doc_count = max(0, int(kb.doc_count or 0) + int(docs_delta or 0))
            kb.chunk_count = max(0, int(kb.chunk_count or 0) + int(chunks_delta or 0))
            db.add(kb)
            db.commit()


kb_service = KnowledgeBaseService()
