from fastapi import APIRouter, Query

from app.schemas.admin import EvolutionSyncResponse
from app.services.evolution_service import evolution_service

router = APIRouter()


@router.post("/rag/evolution/sync-high-quality-posts", response_model=EvolutionSyncResponse)
async def sync_high_quality_posts(
    kb_id: int = Query(default=1),
    min_likes: int = Query(default=30, ge=0),
    min_comments: int = Query(default=5, ge=0),
    limit: int = Query(default=20, ge=1, le=200),
    include_reviewed: bool = Query(default=False),
) -> EvolutionSyncResponse:
    result = evolution_service.sync_high_quality_posts(
        kb_id=kb_id,
        min_likes=min_likes,
        min_comments=min_comments,
        limit=limit,
        include_reviewed=include_reviewed,
    )
    return EvolutionSyncResponse(**result)


@router.get("/rag/evolution/reviews")
async def list_evolution_reviews(limit: int = Query(default=50, ge=1, le=200)) -> dict:
    return {"items": evolution_service.list_reviews(limit=limit)}
