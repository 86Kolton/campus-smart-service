from fastapi import APIRouter

from app.schemas.admin import (
    KnowledgeBaseCreateRequest,
    KnowledgeBaseItem,
    KnowledgeBaseListResponse,
)
from app.schemas.common import MessageResponse
from app.services.kb_service import kb_service

router = APIRouter()


@router.get("/kb", response_model=KnowledgeBaseListResponse)
async def list_kb() -> KnowledgeBaseListResponse:
    return KnowledgeBaseListResponse(items=[KnowledgeBaseItem(**row) for row in kb_service.list_kb()])


@router.post("/kb", response_model=KnowledgeBaseItem)
async def create_kb(payload: KnowledgeBaseCreateRequest) -> KnowledgeBaseItem:
    row = kb_service.create_kb(name=payload.name, description=payload.description)
    return KnowledgeBaseItem(**row)


@router.delete("/kb/{kb_id}", response_model=MessageResponse)
async def delete_kb(kb_id: int) -> MessageResponse:
    ok = kb_service.delete_kb(kb_id)
    return MessageResponse(message="deleted" if ok else "not_found")

