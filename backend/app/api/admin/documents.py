from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from starlette.concurrency import run_in_threadpool

from app.schemas.admin import DocumentContentResponse, DocumentContentUpdateRequest, DocumentItem, DocumentListResponse
from app.schemas.common import MessageResponse
from app.services.document_service import document_service
from app.services.document_upload_service import document_upload_service
from app.services.knowledge_cache_service import knowledge_cache_service
from app.services.kb_service import kb_service
from app.services.task_service import task_service

router = APIRouter()

UPLOAD_422_ERRORS = {
    "document_too_large",
    "document_format_not_supported",
    "document_mime_not_supported",
    "document_encoding_not_supported",
}


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
        if code in UPLOAD_422_ERRORS or (code.startswith("document_") and code != "document_empty"):
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

    task = await run_in_threadpool(
        task_service.create_ingest_task,
        kb_id=kb_id,
        document_id=doc["id"],
        file_ext=str(upload_meta["file_ext"]),
        content=bytes(upload_meta["ingest_content"]),
    )
    return MessageResponse(message=f"uploaded document_id={doc['id']} task_id={task['id']}")


@router.get("/documents/{document_id}/content", response_model=DocumentContentResponse)
async def read_document_content(document_id: int) -> DocumentContentResponse:
    payload = await run_in_threadpool(document_service.read_document_content, document_id)
    if not payload:
        raise HTTPException(status_code=404, detail="document_not_found")
    return DocumentContentResponse(
        document=DocumentItem(**payload["document"]),
        content=str(payload.get("content") or ""),
        editable=bool(payload.get("editable", True)),
    )


@router.put("/documents/{document_id}/content", response_model=MessageResponse)
async def update_document_content(document_id: int, payload: DocumentContentUpdateRequest) -> MessageResponse:
    try:
        doc = await run_in_threadpool(document_service.update_document_content, document_id, payload.content)
    except ValueError as exc:
        code = str(exc)
        status = 422 if code in {"document_too_large", "document_content_required"} else 400
        raise HTTPException(status_code=status, detail=code) from exc
    if not doc:
        raise HTTPException(status_code=404, detail="document_not_found")
    if payload.reindex:
        await run_in_threadpool(
            task_service.create_ingest_task,
            kb_id=int(doc["kb_id"]),
            document_id=int(doc["id"]),
            file_ext=str(doc["file_ext"] or "md"),
            content=str(payload.content or "").encode("utf-8"),
        )
        await run_in_threadpool(knowledge_cache_service.rebuild_chunks)
        return MessageResponse(message=f"updated and reindexed document_id={document_id}")
    return MessageResponse(message=f"updated document_id={document_id}")


@router.delete("/documents/{document_id}", response_model=MessageResponse)
async def delete_document(document_id: int) -> MessageResponse:
    deleted = await run_in_threadpool(document_service.delete_document, document_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="document_not_found")
    await run_in_threadpool(knowledge_cache_service.rebuild_chunks)
    return MessageResponse(message=f"deleted document_id={document_id}")
