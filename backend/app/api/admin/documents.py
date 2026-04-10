from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile

from app.schemas.admin import DocumentItem, DocumentListResponse
from app.schemas.common import MessageResponse
from app.services.document_service import document_service
from app.services.document_upload_service import document_upload_service
from app.services.kb_service import kb_service
from app.services.task_service import task_service

router = APIRouter()


@router.get("/documents", response_model=DocumentListResponse)
async def list_documents(kb_id: int | None = Query(default=None)) -> DocumentListResponse:
    rows = document_service.list_documents(kb_id=kb_id)
    return DocumentListResponse(items=[DocumentItem(**row) for row in rows])


@router.post("/documents/upload", response_model=MessageResponse)
async def upload_document(kb_id: int = Form(...), file: UploadFile = File(...)) -> MessageResponse:
    if not kb_service.exists(kb_id):
        raise HTTPException(status_code=404, detail="knowledge_base_not_found")

    content = await file.read()
    try:
        upload_meta = document_upload_service.save_document(
            content=content,
            file_name=file.filename or "document.txt",
            mime_type=file.content_type or "",
        )
    except ValueError as exc:
        code = str(exc)
        if code in {"document_too_large", "document_format_not_supported", "document_mime_not_supported", "document_encoding_not_supported"}:
            raise HTTPException(status_code=422, detail=code) from exc
        if code == "document_empty":
            raise HTTPException(status_code=400, detail=code) from exc
        raise HTTPException(status_code=400, detail=code) from exc

    doc = document_service.create_document(
        kb_id=kb_id,
        file_name=str(upload_meta["file_name"]),
        file_size=int(upload_meta["file_size"]),
        file_ext=str(upload_meta["file_ext"]),
        mime_type=str(upload_meta["mime_type"]),
        storage_path=str(upload_meta["storage_path"]),
    )

    task = task_service.create_ingest_task(
        kb_id=kb_id,
        document_id=doc["id"],
        file_ext=str(upload_meta["file_ext"]),
        content=content,
    )
    return MessageResponse(message=f"uploaded document_id={doc['id']} task_id={task['id']}")
