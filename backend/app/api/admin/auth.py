from math import ceil
from secrets import compare_digest

from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas.admin import AdminLoginPolicyResponse, AdminLoginRequest, AdminLoginResponse
from app.services.admin_auth_guard_service import admin_auth_guard_service

router = APIRouter()


def _build_guard_detail(code: str, status: dict) -> dict:
    retry_after_seconds = int(status.get("retry_after_seconds", 0) or 0)
    return {
        "code": code,
        "retry_after_seconds": retry_after_seconds,
        "retry_after_minutes": ceil(retry_after_seconds / 60) if retry_after_seconds else 0,
        "remaining_attempts": int(status.get("remaining_attempts", 0) or 0),
        "max_attempts": int(status.get("max_attempts", 0) or 0),
        "lock_minutes": int(status.get("lock_minutes", 0) or 0),
        "window_minutes": int(status.get("window_minutes", 0) or 0),
    }


@router.get("/auth/policy", response_model=AdminLoginPolicyResponse)
async def admin_login_policy() -> AdminLoginPolicyResponse:
    policy = admin_auth_guard_service.get_policy()
    return AdminLoginPolicyResponse(
        max_attempts=int(policy["max_attempts"]),
        lock_minutes=int(policy["lock_minutes"]),
        window_minutes=int(policy["window_minutes"]),
    )


@router.post("/auth/login", response_model=AdminLoginResponse)
async def admin_login(payload: AdminLoginRequest, request: Request) -> AdminLoginResponse:
    username = str(settings.admin_username or "").strip()
    password = str(settings.admin_password or "").strip()
    if not username or not password:
        raise HTTPException(status_code=503, detail="admin_credentials_not_configured")
    guard_status = admin_auth_guard_service.check(request)
    if guard_status["blocked"]:
        raise HTTPException(status_code=429, detail=_build_guard_detail("admin_login_temporarily_blocked", guard_status))
    if not compare_digest(str(payload.username or "").strip(), username) or not compare_digest(
        str(payload.password or "").strip(), password
    ):
        failure = admin_auth_guard_service.record_failure(request)
        if failure["blocked"]:
            raise HTTPException(status_code=429, detail=_build_guard_detail("admin_login_temporarily_blocked", failure))
        raise HTTPException(status_code=401, detail=_build_guard_detail("invalid_admin_credentials", failure))
    admin_auth_guard_service.record_success(request)
    token = create_access_token(subject=username, token_type="admin")
    return AdminLoginResponse(access_token=token)
