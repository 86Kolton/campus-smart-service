from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.evolution_review import EvolutionReview
from app.models.knowledge import KnowledgeDocument
from app.rag.parser.document_parser import document_parser
from app.services.kb_service import kb_service
from app.services.qdrant_service import qdrant_service


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

    def read_document_content(self, document_id: int) -> dict | None:
        with SessionLocal() as db:
            row = db.get(KnowledgeDocument, int(document_id))
            if not row:
                return None
            item = self._to_dict(row)
            storage_path = Path(str(row.storage_path or "").strip())

        if not storage_path.exists() or not storage_path.is_file():
            item["content_missing"] = True
            return {"document": item, "content": "", "editable": False}
        try:
            content = storage_path.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            try:
                content = document_parser.parse_bytes(storage_path.read_bytes(), str(item.get("file_ext") or ""))
            except ValueError:
                return {"document": item, "content": "", "editable": False}
        return {"document": item, "content": content, "editable": True}

    def update_document_content(self, document_id: int, content: str) -> dict | None:
        safe_content = str(content or "").strip()
        if not safe_content:
            raise ValueError("document_content_required")
        if len(safe_content.encode("utf-8")) > 2 * 1024 * 1024:
            raise ValueError("document_too_large")

        with SessionLocal() as db:
            row = db.get(KnowledgeDocument, int(document_id))
            if not row:
                return None
            raw_storage_path = str(row.storage_path or "").strip()
            if not raw_storage_path:
                raise ValueError("document_storage_missing")
            storage_path = Path(raw_storage_path)
            target_path = storage_path
            if storage_path.suffix.lower() not in {".md", ".txt", ".csv", ".json", ".log"}:
                target_path = storage_path.with_suffix(".md")
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(safe_content + "\n", encoding="utf-8")
            if target_path != storage_path:
                try:
                    storage_path.unlink(missing_ok=True)
                except OSError:
                    pass
            row.storage_path = str(target_path.resolve())
            row.file_size = target_path.stat().st_size
            row.file_ext = "md"
            row.mime_type = "text/markdown"
            row.status = "uploaded"
            row.error_message = ""
            db.add(row)
            db.commit()
            db.refresh(row)
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

    def delete_document(self, document_id: int) -> dict | None:
        with SessionLocal() as db:
            doc = db.get(KnowledgeDocument, int(document_id))
            if not doc:
                return None
            item = self._to_dict(doc)
            kb_id = int(doc.kb_id)
            chunk_count = int(doc.chunk_count or 0)
            storage_path = str(doc.storage_path or "")
            rows = db.execute(select(EvolutionReview).where(EvolutionReview.document_id == int(document_id))).scalars().all()
            for review in rows:
                review.document_id = None
                db.add(review)
            db.delete(doc)
            db.commit()

        qdrant_service.delete_document_chunks(kb_id=kb_id, document_id=int(document_id))
        if storage_path:
            try:
                Path(storage_path).unlink(missing_ok=True)
            except OSError:
                pass
        kb_service.bump_stats(kb_id, docs_delta=-1, chunks_delta=-chunk_count)
        return item


document_service = DocumentService()
