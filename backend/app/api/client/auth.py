from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import ClientIdentity, require_client_identity, require_wechat_bound_client
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_access_token
from app.schemas.client import (
    ClientLoginRequest,
    ClientLoginResponse,
    ClientMeResponse,
    ClientLogoutRequest,
    ClientRefreshRequest,
    ClientRegisterRequest,
    WebLoginCodeResponse,
    WebLoginExchangeRequest,
    WechatBindRequest,
    WechatLoginRequest,
)
from app.services.token_service import token_service
from app.services.user_service import user_service
from app.services.wechat_service import wechat_service
from app.services.web_login_code_service import web_login_code_service

router = APIRouter()
bearer_scheme = HTTPBearer(auto_error=False)
WEB_SESSION_MINUTES = 60


def _bind_state(wechat_bound: bool) -> str:
    return "已绑定微信身份" if wechat_bound else "未绑定微信身份"


def _issue_client_tokens(
    user_id: int,
    username: str,
    display_name: str,
    session_type: str = "app",
    access_minutes: int | None = None,
    refresh_minutes: int | None = None,
) -> ClientLoginResponse:
    user = user_service.get_user(int(user_id))
    public_name = user_service.get_public_name(user) if user else user_service.build_default_public_name(display_name)
    wechat_bound = bool(user and str(user.wechat_openid or "").strip())
    safe_session_type = str(session_type or "app").strip() or "app"
    access_token = create_access_token(
        subject=username,
        token_type="client",
        extra={"uid": int(user_id), "sid": safe_session_type},
        expire_minutes=access_minutes,
    )
    refresh_token = create_refresh_token(
        subject=username,
        extra={"uid": int(user_id), "sid": safe_session_type},
        expire_minutes=refresh_minutes,
    )
    refresh_payload = decode_access_token(refresh_token)
    refresh_jti = str(refresh_payload.get("jti", "")).strip()
    if refresh_minutes is not None:
        expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=int(refresh_minutes))
    else:
        expires_at = datetime.now(tz=timezone.utc) + timedelta(days=int(settings.jwt_refresh_days))
    if refresh_jti:
        token_service.store_refresh_token(user_id=int(user_id), jti=refresh_jti, expires_at=expires_at)

    return ClientLoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        session_type=safe_session_type,
        expires_in=int(access_minutes or settings.jwt_expire_minutes) * 60,
        user_id=int(user_id),
        username=username,
        display_name=display_name,
        public_name=public_name,
        wechat_bound=wechat_bound,
        bind_state=_bind_state(wechat_bound),
    )


def _raise_wechat_error(exc: ValueError) -> None:
    code = str(exc)
    if code in {"wechat_code_required"}:
        raise HTTPException(status_code=400, detail=code) from exc
    if code in {"wechat_not_configured"}:
        raise HTTPException(status_code=503, detail=code) from exc
    if code.startswith("wechat_code2session_"):
        raise HTTPException(status_code=401, detail=code) from exc
    raise HTTPException(status_code=502, detail=code or "wechat_exchange_failed") from exc


@router.post("/auth/login", response_model=ClientLoginResponse)
async def client_login(payload: ClientLoginRequest) -> ClientLoginResponse:
    user = user_service.authenticate_client(payload.username, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="invalid_client_credentials")
    return _issue_client_tokens(
        user_id=int(user.id),
        username=user.username,
        display_name=user.display_name,
    )


@router.post("/auth/register", response_model=ClientLoginResponse)
async def client_register(payload: ClientRegisterRequest) -> ClientLoginResponse:
    try:
        user = user_service.register_client(
            username=payload.username,
            display_name=payload.display_name,
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _issue_client_tokens(
        user_id=int(user.id),
        username=user.username,
        display_name=user.display_name,
    )


@router.get("/auth/me", response_model=ClientMeResponse)
async def client_me(identity: ClientIdentity = Depends(require_client_identity)) -> ClientMeResponse:
    user = user_service.get_user(identity.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="client_not_found")
    return ClientMeResponse(
        user_id=int(user.id),
        username=user.username,
        display_name=user_service.get_visible_profile_name(user),
        public_name=user_service.get_public_name(user),
        wechat_bound=bool(str(user.wechat_openid or "").strip()),
        bind_state=_bind_state(bool(str(user.wechat_openid or "").strip())),
        role=user.role,
        status=user.status,
    )


@router.post("/auth/refresh", response_model=ClientLoginResponse)
async def client_refresh(payload: ClientRefreshRequest) -> ClientLoginResponse:
    raw = decode_access_token(payload.refresh_token)
    err = raw.get("_error")
    if err:
        raise HTTPException(status_code=401, detail=err)
    if str(raw.get("typ", "")) != "client_refresh":
        raise HTTPException(status_code=401, detail="refresh_token_invalid")
    jti = str(raw.get("jti", "")).strip()
    username = str(raw.get("sub", "")).strip()
    try:
        user_id = int(raw.get("uid"))
    except Exception as exc:
        raise HTTPException(status_code=401, detail="refresh_token_invalid") from exc
    if not jti or not username or user_id <= 0:
        raise HTTPException(status_code=401, detail="refresh_token_invalid")
    session_type = str(raw.get("sid", "") or "app").strip() or "app"
    if session_type == "web":
        raise HTTPException(status_code=401, detail="web_session_relogin_required")
    if not token_service.is_refresh_token_valid(jti=jti, user_id=user_id):
        raise HTTPException(status_code=401, detail="refresh_token_revoked")

    token_service.revoke_refresh_token(jti)

    user = user_service.get_user(user_id)
    display_name = user.display_name if user else username
    return _issue_client_tokens(
        user_id=int(user_id),
        username=username,
        display_name=display_name,
        session_type=session_type,
    )


@router.post("/auth/logout")
async def client_logout(
    payload: ClientLogoutRequest,
    identity: ClientIdentity = Depends(require_client_identity),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="client_token_required")
    access_payload = decode_access_token(credentials.credentials)
    err = access_payload.get("_error")
    if err:
        raise HTTPException(status_code=401, detail=err)
    jti = str(access_payload.get("jti", "")).strip()
    exp = access_payload.get("exp")
    if not jti or not exp:
        raise HTTPException(status_code=401, detail="client_token_invalid")
    if isinstance(exp, (int, float)):
        expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
    else:
        expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    token_service.revoke_access_token(jti=jti, token_type="client", expires_at=expires_at)
    if payload.refresh_token:
        refresh_payload = decode_access_token(payload.refresh_token)
        refresh_jti = str(refresh_payload.get("jti", "")).strip()
        if refresh_jti:
            token_service.revoke_refresh_token(refresh_jti)
    return {"ok": True}


@router.post("/auth/logout-web-sessions")
async def client_logout_web_sessions(
    identity: ClientIdentity = Depends(require_wechat_bound_client),
) -> dict:
    now = datetime.now(tz=timezone.utc)
    token_service.revoke_client_session_before(
        user_id=identity.user_id,
        session_type="web",
        before=now,
        expires_at=now + timedelta(minutes=WEB_SESSION_MINUTES + 5),
    )
    # Existing web refresh tokens from earlier builds were not session-tagged, so
    # revoke refresh tokens too. The mini program can silently re-login with WeChat.
    token_service.revoke_all_refresh_tokens(identity.user_id)
    return {"ok": True, "message": "web_sessions_logged_out"}


@router.post("/auth/wechat/login", response_model=ClientLoginResponse)
async def client_wechat_login(payload: WechatLoginRequest) -> ClientLoginResponse:
    code = str(payload.code or "").strip()
    try:
        openid, _ = await wechat_service.code_to_openid(code)
    except ValueError as exc:
        _raise_wechat_error(exc)
    user = user_service.get_or_create_by_openid(openid, payload.display_name)

    return _issue_client_tokens(
        user_id=int(user.id),
        username=user.username,
        display_name=user.display_name,
    )


@router.post("/auth/wechat/bind")
async def client_wechat_bind(
    payload: WechatBindRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> dict:
    code = str(payload.code or "").strip()
    try:
        openid, _ = await wechat_service.code_to_openid(code)
    except ValueError as exc:
        _raise_wechat_error(exc)
    try:
        user_service.bind_openid(identity.user_id, openid)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"ok": True, "openid": openid}


@router.post("/auth/web-login-code", response_model=WebLoginCodeResponse)
async def create_web_login_code(
    identity: ClientIdentity = Depends(require_wechat_bound_client),
) -> WebLoginCodeResponse:
    return WebLoginCodeResponse(**web_login_code_service.create_code(user_id=identity.user_id))


@router.post("/auth/web-login-exchange", response_model=ClientLoginResponse)
async def exchange_web_login_code(payload: WebLoginExchangeRequest) -> ClientLoginResponse:
    try:
        user = web_login_code_service.consume_code(payload.code)
    except ValueError as exc:
        code = str(exc)
        if code in {"web_login_code_required"}:
            raise HTTPException(status_code=400, detail=code) from exc
        if code in {"web_login_code_invalid", "web_login_code_expired"}:
            raise HTTPException(status_code=401, detail=code) from exc
        if code == "client_not_found":
            raise HTTPException(status_code=404, detail=code) from exc
        raise HTTPException(status_code=400, detail=code) from exc
    return _issue_client_tokens(
        user_id=int(user.id),
        username=user.username,
        display_name=user.display_name,
        session_type="web",
        access_minutes=WEB_SESSION_MINUTES,
        refresh_minutes=WEB_SESSION_MINUTES,
    )
