from fastapi import APIRouter, Depends, Query

from app.api.deps import ClientIdentity, require_client_identity
from app.schemas.client import (
    SearchPostsResponse,
    SearchRecentCreateRequest,
    SearchRecentResponse,
)
from app.schemas.common import MessageResponse
from app.services.search_service import search_service

router = APIRouter()


@router.get("/search/posts", response_model=SearchPostsResponse)
async def search_posts(
    q: str = Query(default=""),
    sort: str = Query(default="hot"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=30, ge=1, le=50),
    _identity: ClientIdentity = Depends(require_client_identity),
) -> SearchPostsResponse:
    items = search_service.search_posts(keyword=q, sort=sort)
    start = max(0, (page - 1) * page_size)
    end = start + page_size
    sliced = items[start:end]
    total = len(items)
    has_more = end < total
    return SearchPostsResponse(
        page=page,
        page_size=page_size,
        total=total,
        has_more=has_more,
        items=sliced,
    )


@router.get("/search/recent", response_model=SearchRecentResponse)
async def get_recent_searches(identity: ClientIdentity = Depends(require_client_identity)) -> SearchRecentResponse:
    return SearchRecentResponse(keywords=search_service.get_recent(user_id=identity.user_id))


@router.post("/search/recent", response_model=MessageResponse)
async def save_recent_search(
    payload: SearchRecentCreateRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> MessageResponse:
    search_service.save_recent(payload.keyword, user_id=identity.user_id)
    return MessageResponse(message="ok")


@router.delete("/search/recent", response_model=MessageResponse)
async def clear_recent_searches(identity: ClientIdentity = Depends(require_client_identity)) -> MessageResponse:
    search_service.clear_recent(user_id=identity.user_id)
    return MessageResponse(message="ok")
