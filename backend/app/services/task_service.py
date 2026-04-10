from __future__ import annotations

from datetime import datetime
from pathlib import Path

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.task import IngestTask
from app.services.document_service import document_service
from app.services.ingest_service import ingest_service


class TaskService:
    def _to_dict(self, row: IngestTask) -> dict:
        return {
            "id": int(row.id),
            "kb_id": int(row.kb_id),
            "document_id": int(row.document_id),
            "task_type": row.task_type,
            "status": row.status,
            "retry_count": int(row.retry_count or 0),
            "error_message": row.error_message,
            "created_at": row.created_at.isoformat() if row.created_at else datetime.utcnow().isoformat(),
        }

    def list_tasks(self) -> list[dict]:
        with SessionLocal() as db:
            rows = db.execute(select(IngestTask).order_by(IngestTask.id.asc())).scalars().all()
        return [self._to_dict(row) for row in rows]

    def get_task(self, task_id: int) -> dict | None:
        with SessionLocal() as db:
            row = db.get(IngestTask, task_id)
            if not row:
                return None
            return self._to_dict(row)

    def _update_task(self, task_id: int, **kwargs) -> dict | None:
        with SessionLocal() as db:
            row = db.get(IngestTask, task_id)
            if not row:
                return None
            for key, value in kwargs.items():
                setattr(row, key, value)
            db.add(row)
            db.commit()
            db.refresh(row)
            return self._to_dict(row)

    def create_ingest_task(self, kb_id: int, document_id: int, file_ext: str, content: bytes) -> dict:
        with SessionLocal() as db:
            next_id = int(db.scalar(select(func.max(IngestTask.id))) or 0) + 1
            row = IngestTask(
                id=next_id,
                kb_id=kb_id,
                document_id=document_id,
                task_type="ingest",
                status="running",
                retry_count=0,
                error_message="",
            )
            db.add(row)
            db.commit()

        task = self._run_ingest_task(task_id=next_id, kb_id=kb_id, document_id=document_id, file_ext=file_ext, content=content)
        return task or {
            "id": next_id,
            "kb_id": kb_id,
            "document_id": document_id,
            "task_type": "ingest",
            "status": "failed",
            "retry_count": 0,
            "error_message": "task update failed",
            "created_at": datetime.utcnow().isoformat(),
        }

    def _run_ingest_task(self, task_id: int, kb_id: int, document_id: int, file_ext: str, content: bytes) -> dict | None:
        try:
            ingest_service.ingest_document(
                kb_id=kb_id,
                document_id=document_id,
                file_ext=file_ext,
                content=content,
            )
            return self._update_task(task_id, status="success", error_message="")
        except Exception as exc:
            return self._update_task(task_id, status="failed", error_message=str(exc))

    def retry_task(self, task_id: int, content: bytes | None = None) -> dict | None:
        task = self.get_task(task_id)
        if not task:
            return None

        doc = document_service.get_document(task["document_id"])
        if not doc:
            return self._update_task(task_id, status="failed", error_message="document not found")

        payload = content if content is not None else b""
        if not payload:
            storage_path = str(doc.get("storage_path", "")).strip()
            path = Path(storage_path)
            if storage_path and path.exists() and path.is_file():
                payload = path.read_bytes()
            else:
                payload = f"Retry placeholder for {doc['file_name']}".encode("utf-8")

        self._update_task(task_id, status="running", retry_count=int(task.get("retry_count", 0)) + 1, error_message="")
        return self._run_ingest_task(
            task_id=task_id,
            kb_id=int(task["kb_id"]),
            document_id=int(task["document_id"]),
            file_ext=str(doc["file_ext"]),
            content=payload,
        )


task_service = TaskService()
