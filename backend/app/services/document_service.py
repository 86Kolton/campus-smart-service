from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.knowledge import KnowledgeDocument
from app.services.kb_service import kb_service


class DocumentService:
    def _to_dict(self, row: KnowledgeDocument) -> dict:
        return {
            "id": int(row.id),
            "kb_id": int(row.kb_id),
            "file_name": row.file_name,
            "file_ext": row.file_ext,
            "file_size": int(row.file_size or 0),
            "mime_type": row.mime_type,
            "storage_path": row.storage_path,
            "status": row.status,
            "chunk_count": int(row.chunk_count or 0),
            "error_message": row.error_message,
            "uploaded_by": int(row.uploaded_by),
            "created_at": row.created_at.isoformat() if row.created_at else datetime.utcnow().isoformat(),
        }

    def list_documents(self, kb_id: int | None = None) -> list[dict]:
        with SessionLocal() as db:
            stmt = select(KnowledgeDocument).order_by(KnowledgeDocument.id.desc())
            if kb_id is not None:
                stmt = stmt.where(KnowledgeDocument.kb_id == kb_id)
            rows = db.execute(stmt).scalars().all()
        return [self._to_dict(row) for row in rows]

    def get_document(self, document_id: int) -> dict | None:
        with SessionLocal() as db:
            row = db.get(KnowledgeDocument, document_id)
            if not row:
                return None
            return self._to_dict(row)

    def create_document(
        self,
        kb_id: int,
        file_name: str,
        file_size: int,
        file_ext: str,
        mime_type: str,
        storage_path: str | None = None,
    ) -> dict:
        with SessionLocal() as db:
            next_id = int(db.scalar(select(func.max(KnowledgeDocument.id))) or 0) + 1
            row = KnowledgeDocument(
                id=next_id,
                kb_id=kb_id,
                file_name=file_name,
                file_ext=file_ext,
                file_size=file_size,
                mime_type=mime_type,
                storage_path=storage_path or f"/data/uploads/{file_name}",
                status="uploaded",
                chunk_count=0,
                error_message="",
                uploaded_by=1,
            )
            db.add(row)
            db.commit()
            db.refresh(row)

        kb_service.bump_stats(kb_id, docs_delta=1)
        return self._to_dict(row)

    def update_status(self, document_id: int, status: str, error_message: str = "") -> None:
        with SessionLocal() as db:
            doc = db.get(KnowledgeDocument, document_id)
            if not doc:
                return
            doc.status = status
            doc.error_message = error_message
            db.add(doc)
            db.commit()

    def set_chunk_count(self, document_id: int, chunk_count: int) -> None:
        with SessionLocal() as db:
            doc = db.get(KnowledgeDocument, document_id)
            if not doc:
                return
            before = int(doc.chunk_count or 0)
            delta = int(chunk_count) - before
            doc.chunk_count = int(chunk_count)
            db.add(doc)
            db.commit()
            kb_id = int(doc.kb_id)

        kb_service.bump_stats(kb_id, chunks_delta=delta)


document_service = DocumentService()
