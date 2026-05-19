from fastapi import APIRouter, HTTPException, Query
from starlette.concurrency import run_in_threadpool

from app.schemas.admin import AdoptCommentRequest, AdoptCommentResponse, AdoptionListResponse, AdoptionRepairResponse
from app.services.post_service import post_service

router = APIRouter()


@router.post("/feed/adopt-comment", response_model=AdoptCommentResponse)
async def adopt_comment(payload: AdoptCommentRequest) -> AdoptCommentResponse:
    try:
        result = await run_in_threadpool(
            post_service.adopt_comment,
            post_id=payload.post_id,
            comment_id=payload.comment_id,
            prune_other_comments=payload.prune_other_comments,
            hard_delete=payload.hard_delete,
        )
    except ValueError as exc:
        detail = str(exc)
        status = 404 if detail in {"post_not_found", "comment_not_found"} else 400
        raise HTTPException(status_code=status, detail=detail) from exc
    return AdoptCommentResponse(**result)


@router.get("/feed/adoptions", response_model=AdoptionListResponse)
async def list_adoptions() -> AdoptionListResponse:
    return AdoptionListResponse(items=await run_in_threadpool(post_service.list_adoptions))


@router.post("/feed/adoptions/repair", response_model=AdoptionRepairResponse)
async def repair_missing_adoptions(limit: int = Query(default=500, ge=1, le=1000)) -> AdoptionRepairResponse:
    return AdoptionRepairResponse(**await run_in_threadpool(post_service.repair_missing_adoptions, limit=limit))
