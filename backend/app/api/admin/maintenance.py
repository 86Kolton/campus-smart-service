from fastapi import APIRouter, Query

from app.schemas.admin import CleanupStalePostsResponse
from app.services.maintenance_service import maintenance_service

router = APIRouter()


@router.post("/maintenance/cleanup-stale-posts", response_model=CleanupStalePostsResponse)
async def cleanup_stale_posts(days: int = Query(default=7, ge=1, le=60)) -> CleanupStalePostsResponse:
    result = maintenance_service.cleanup_stale_unadopted_posts(days=days)
    return CleanupStalePostsResponse(**result)
