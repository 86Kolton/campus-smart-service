from datetime import datetime, timedelta, timezone
import secrets
from typing import Any

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core.config import settings


def _new_jti() -> str:
    return secrets.token_hex(16)


def create_access_token(
    subject: str,
    token_type: str = "admin",
    extra: dict[str, Any] | None = None,
    expire_minutes: int | None = None,
    jti: str | None = None,
) -> str:
    ttl = expire_minutes if expire_minutes is not None else settings.jwt_expire_minutes
    now = datetime.now(tz=timezone.utc)
    expire = now + timedelta(minutes=int(ttl))
    payload: dict[str, Any] = {
        "sub": subject,
        "typ": token_type,
        "iat": int(now.timestamp()),
        "exp": expire,
        "jti": jti or _new_jti(),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_refresh_token(
    subject: str,
    extra: dict[str, Any] | None = None,
    jti: str | None = None,
    expire_days: int | None = None,
    expire_minutes: int | None = None,
) -> str:
    now = datetime.now(tz=timezone.utc)
    if expire_minutes is not None:
        expire = now + timedelta(minutes=int(expire_minutes))
    else:
        expire = now + timedelta(days=int(expire_days if expire_days is not None else settings.jwt_refresh_days))
    payload: dict[str, Any] = {
        "sub": subject,
        "typ": "client_refresh",
        "iat": int(now.timestamp()),
        "exp": expire,
        "jti": jti or _new_jti(),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    try:
        data = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        if not isinstance(data, dict):
            return {}
        return data
    except ExpiredSignatureError:
        return {"_error": "token_expired"}
    except InvalidTokenError:
        return {"_error": "token_invalid"}
