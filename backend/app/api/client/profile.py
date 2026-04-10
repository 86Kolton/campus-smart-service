from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import ClientIdentity, require_client_identity
from app.schemas.client import (
    ProfileSettingsResponse,
    ProfileSummaryResponse,
    UpdatePublicNameRequest,
    UpdatePublicNameResponse,
)
from app.services.profile_service import profile_service
from app.services.user_service import user_service

router = APIRouter()


@router.get("/profile/summary", response_model=ProfileSummaryResponse)
async def profile_summary(identity: ClientIdentity = Depends(require_client_identity)) -> ProfileSummaryResponse:
    return ProfileSummaryResponse(**profile_service.summary(user_id=identity.user_id))


@router.get("/profile/settings", response_model=ProfileSettingsResponse)
async def profile_settings(identity: ClientIdentity = Depends(require_client_identity)) -> ProfileSettingsResponse:
    user = user_service.get_user(identity.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="client_not_found")
    wechat_bound = bool(user.wechat_openid)
    bind_state = "已绑定微信身份" if wechat_bound else "未绑定微信身份"
    return ProfileSettingsResponse(
        display_name=user_service.get_visible_profile_name(user),
        public_name=user_service.get_public_name(user),
        bind_state=bind_state,
        wechat_bound=wechat_bound,
    )


@router.post("/profile/public-name", response_model=UpdatePublicNameResponse)
async def update_public_name(
    payload: UpdatePublicNameRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> UpdatePublicNameResponse:
    try:
        user = user_service.update_public_name(identity.user_id, payload.public_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return UpdatePublicNameResponse(public_name=user_service.get_public_name(user))
