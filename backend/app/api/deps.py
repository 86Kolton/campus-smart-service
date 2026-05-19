from dataclasses import dataclass

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings
from app.core.security import decode_access_token
from app.services.token_service import token_service
from app.services.user_service import user_service


bearer_scheme = HTTPBearer(auto_error=False)


@dataclass(slots=True)
class ClientIdentity:
    user_id: int
    username: str
    wechat_bound: bool = False


def require_admin_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="admin_token_required")

    payload = decode_access_token(credentials.credentials)
    err = payload.get("_error")
    if err:
        raise HTTPException(status_code=401, detail=err)

    token_type = str(payload.get("typ", "")).strip()
    subject = str(payload.get("sub", "")).strip()
    jti = str(payload.get("jti", "")).strip()
    if token_type and token_type != "admin":
        raise HTTPException(status_code=403, detail="admin_forbidden")
    if not jti:
        raise HTTPException(status_code=401, detail="admin_token_invalid")
    if token_service.is_token_revoked(jti):
        raise HTTPException(status_code=401, detail="admin_token_revoked")
    expected_subject = str(settings.admin_username or "admin").strip() or "admin"
    if subject != expected_subject:
        raise HTTPException(status_code=403, detail="admin_forbidden")
    return subject


def require_client_identity(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> ClientIdentity:
    if not credentials or not credentials.credentials:
        raise HTTPException(status_code=401, detail="client_token_required")

    payload = decode_access_token(credentials.credentials)
    err = payload.get("_error")
    if err:
        raise HTTPException(status_code=401, detail=err)

    token_type = str(payload.get("typ", "")).strip()
    if token_type and token_type != "client":
        raise HTTPException(status_code=403, detail="client_forbidden")

    username = str(payload.get("sub", "")).strip()
    jti = str(payload.get("jti", "")).strip()
    try:
        user_id = int(payload.get("uid"))
    except Exception as exc:
        raise HTTPException(status_code=401, detail="client_token_invalid") from exc

    if user_id <= 0 or not username or not jti:
        raise HTTPException(status_code=401, detail="client_token_invalid")
    if token_service.is_token_revoked(jti):
        raise HTTPException(status_code=401, detail="client_token_revoked")

    return ClientIdentity(user_id=user_id, username=username)


def require_wechat_bound_client(
    identity: ClientIdentity = Depends(require_client_identity),
) -> ClientIdentity:
    user = user_service.get_user(identity.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="client_not_found")
    if user.role != "client" or user.status != "active":
        raise HTTPException(status_code=403, detail="client_forbidden")
    if not str(user.wechat_openid or "").strip():
        raise HTTPException(status_code=403, detail="wechat_bind_required")
    return ClientIdentity(user_id=identity.user_id, username=identity.username, wechat_bound=True)
