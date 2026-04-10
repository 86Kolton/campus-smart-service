from app.services.ingest_service import ingest_service
from app.tasks.celery_app import celery_app


@celery_app.task(name="ingest.document")
def ingest_document_task(kb_id: int, document_id: int, file_ext: str, content: str) -> int:
    payload = content.encode("utf-8")
    return ingest_service.ingest_document(kb_id=kb_id, document_id=document_id, file_ext=file_ext, content=payload)

