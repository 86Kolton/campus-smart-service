from fastapi import APIRouter, Depends

from app.api.deps import ClientIdentity, require_client_identity
from app.schemas.client import (
    MarkReadRequest,
    MessageListResponse,
    UnreadCountResponse,
)
from app.schemas.common import MessageResponse
from app.services.message_service import message_service

router = APIRouter()


@router.get("/messages/unread-count", response_model=UnreadCountResponse)
async def unread_count(identity: ClientIdentity = Depends(require_client_identity)) -> UnreadCountResponse:
    return UnreadCountResponse(**message_service.unread_count(user_id=identity.user_id))


@router.get("/messages/likes", response_model=MessageListResponse)
async def list_likes(identity: ClientIdentity = Depends(require_client_identity)) -> MessageListResponse:
    return MessageListResponse(items=message_service.list_likes(user_id=identity.user_id))


@router.get("/messages/saved", response_model=MessageListResponse)
async def list_saved(identity: ClientIdentity = Depends(require_client_identity)) -> MessageListResponse:
    return MessageListResponse(items=message_service.list_saved(user_id=identity.user_id))


@router.post("/messages/mark-read", response_model=MessageResponse)
async def mark_read(
    payload: MarkReadRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> MessageResponse:
    message_service.mark_read(payload.type, user_id=identity.user_id)
    return MessageResponse(message="ok")
