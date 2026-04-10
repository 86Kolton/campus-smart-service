from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import ClientIdentity, require_client_identity
from app.schemas.client import (
    CreateErrandRequest,
    CreateErrandResponse,
    ErrandListResponse,
    UpdateErrandStatusRequest,
    UpdateErrandStatusResponse,
)
from app.services.errand_service import errand_service

router = APIRouter()


def _map_errand_error(exc: ValueError) -> HTTPException:
    code = str(exc)
    if code == "errand_not_found":
        return HTTPException(status_code=404, detail=code)
    if code in {
        "errand_claim_self_forbidden",
        "errand_deliver_forbidden",
        "errand_confirm_forbidden",
        "errand_cancel_forbidden",
        "errand_delete_forbidden",
    }:
        return HTTPException(status_code=403, detail=code)
    if code == "errand_status_conflict":
        return HTTPException(status_code=409, detail=code)
    if code in {
        "errand_title_required",
        "errand_pickup_required",
        "errand_destination_required",
        "errand_contact_required",
    }:
        return HTTPException(status_code=422, detail=code)
    return HTTPException(status_code=400, detail=code)


@router.get("/errands", response_model=ErrandListResponse)
async def list_errands(identity: ClientIdentity = Depends(require_client_identity)) -> ErrandListResponse:
    return ErrandListResponse(items=errand_service.list_tasks(viewer_user_id=identity.user_id))


@router.get("/errands/my", response_model=ErrandListResponse)
async def list_my_errands(identity: ClientIdentity = Depends(require_client_identity)) -> ErrandListResponse:
    return ErrandListResponse(items=errand_service.list_my_tasks(viewer_user_id=identity.user_id))


@router.post("/errands", response_model=CreateErrandResponse)
async def create_errand(
    payload: CreateErrandRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> CreateErrandResponse:
    try:
        item = errand_service.create_task(
            publisher_id=identity.user_id,
            task_type=payload.task_type,
            title=payload.title,
            reward=payload.reward,
            time_text=payload.time,
            pickup_location=payload.pickup_location,
            destination=payload.destination,
            note=payload.note,
            contact=payload.contact,
        )
    except ValueError as exc:
        raise _map_errand_error(exc) from exc
    return CreateErrandResponse(**item)


@router.post("/errands/action", response_model=UpdateErrandStatusResponse)
async def update_errand_status(
    payload: UpdateErrandStatusRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> UpdateErrandStatusResponse:
    try:
        result = errand_service.apply_action(task_id=payload.task_id, action=payload.action, user_id=identity.user_id)
    except ValueError as exc:
        raise _map_errand_error(exc) from exc
    return UpdateErrandStatusResponse(**result)
