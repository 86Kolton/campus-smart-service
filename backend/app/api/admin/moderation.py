from fastapi import APIRouter, HTTPException

from app.schemas.admin import AdoptCommentRequest, AdoptCommentResponse, AdoptionListResponse
from app.services.post_service import post_service

router = APIRouter()


@router.post("/feed/adopt-comment", response_model=AdoptCommentResponse)
async def adopt_comment(payload: AdoptCommentRequest) -> AdoptCommentResponse:
    try:
        result = post_service.adopt_comment(
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
    return AdoptionListResponse(items=post_service.list_adoptions())
