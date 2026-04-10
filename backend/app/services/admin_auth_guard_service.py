from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256

from fastapi import Request
from sqlalchemy import func, select

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.admin_login_guard import AdminLoginGuard


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _safe_dt(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


class AdminAuthGuardService:
    def _limits(self) -> tuple[int, int, int]:
        max_attempts = max(2, int(settings.admin_login_max_attempts or 5))
        lock_minutes = max(1, int(settings.admin_login_lock_minutes or 20))
        window_minutes = max(1, int(settings.admin_login_window_minutes or 10))
        return max_attempts, lock_minutes, window_minutes

    def get_policy(self) -> dict:
        max_attempts, lock_minutes, window_minutes = self._limits()
        return {
            "max_attempts": max_attempts,
            "lock_minutes": lock_minutes,
            "window_minutes": window_minutes,
        }

    def _extract_ip(self, request: Request) -> str:
        forwarded = str(request.headers.get("x-forwarded-for", "")).strip()
        if forwarded:
            return forwarded.split(",")[0].strip()
        client = getattr(request, "client", None)
        return str(getattr(client, "host", "") or "").strip() or "unknown"

    def _fingerprint(self, request: Request) -> tuple[str, str, str]:
        ip_address = self._extract_ip(request)
        user_agent = str(request.headers.get("user-agent", "")).strip()
        ua_hash = sha256(user_agent.encode("utf-8")).hexdigest()
        fingerprint = sha256(f"{ip_address}|{user_agent}".encode("utf-8")).hexdigest()
        return fingerprint, ip_address, ua_hash

    def _reset_row(self, row: AdminLoginGuard, now: datetime) -> None:
        row.failed_count = 0
        row.first_failed_at = None
        row.last_failed_at = None
        row.lock_until = None
        row.last_success_at = now

    def check(self, request: Request) -> dict:
        max_attempts, lock_minutes, window_minutes = self._limits()
        fingerprint, _, _ = self._fingerprint(request)
        now = _utcnow()
        base = {
            "blocked": False,
            "retry_after_seconds": 0,
            "remaining_attempts": max_attempts,
            "max_attempts": max_attempts,
            "lock_minutes": lock_minutes,
            "window_minutes": window_minutes,
        }
        with SessionLocal() as db:
            row = db.execute(select(AdminLoginGuard).where(AdminLoginGuard.fingerprint == fingerprint)).scalar_one_or_none()
            if row is None:
                return base

            lock_until = _safe_dt(row.lock_until)
            if lock_until and lock_until > now:
                return {
                    **base,
                    "blocked": True,
                    "retry_after_seconds": max(1, int((lock_until - now).total_seconds())),
                    "remaining_attempts": 0,
                }

            if lock_until and lock_until <= now:
                self._reset_row(row, now)
                db.add(row)
                db.commit()
                return base

            first_failed_at = _safe_dt(row.first_failed_at)
            if not first_failed_at or first_failed_at < now - timedelta(minutes=window_minutes):
                self._reset_row(row, now)
                db.add(row)
                db.commit()
                return base

            base["remaining_attempts"] = max(0, max_attempts - int(row.failed_count or 0))

        return base

    def record_failure(self, request: Request) -> dict:
        fingerprint, ip_address, ua_hash = self._fingerprint(request)
        now = _utcnow()
        max_attempts, lock_minutes, window_minutes = self._limits()
        window_start = now - timedelta(minutes=window_minutes)

        with SessionLocal() as db:
            row = db.execute(select(AdminLoginGuard).where(AdminLoginGuard.fingerprint == fingerprint)).scalar_one_or_none()
            if row is None:
                next_id = int(db.scalar(select(func.max(AdminLoginGuard.id))) or 0) + 1
                row = AdminLoginGuard(
                    id=next_id,
                    fingerprint=fingerprint,
                    ip_address=ip_address,
                    user_agent_hash=ua_hash,
                    failed_count=0,
                )

            first_failed_at = _safe_dt(row.first_failed_at)
            if not first_failed_at or first_failed_at < window_start:
                row.failed_count = 0
                row.first_failed_at = now

            row.ip_address = ip_address
            row.user_agent_hash = ua_hash
            row.failed_count = int(row.failed_count or 0) + 1
            row.last_failed_at = now

            blocked = False
            retry_after_seconds = 0
            remaining_attempts = max(0, max_attempts - int(row.failed_count or 0))
            if int(row.failed_count or 0) >= max_attempts:
                row.lock_until = now + timedelta(minutes=lock_minutes)
                blocked = True
                retry_after_seconds = lock_minutes * 60
                remaining_attempts = 0

            db.add(row)
            db.commit()

        return {
            "blocked": blocked,
            "retry_after_seconds": retry_after_seconds,
            "remaining_attempts": remaining_attempts,
            "max_attempts": max_attempts,
            "lock_minutes": lock_minutes,
            "window_minutes": window_minutes,
        }

    def record_success(self, request: Request) -> None:
        fingerprint, ip_address, ua_hash = self._fingerprint(request)
        now = _utcnow()
        with SessionLocal() as db:
            row = db.execute(select(AdminLoginGuard).where(AdminLoginGuard.fingerprint == fingerprint)).scalar_one_or_none()
            if row is None:
                next_id = int(db.scalar(select(func.max(AdminLoginGuard.id))) or 0) + 1
                row = AdminLoginGuard(
                    id=next_id,
                    fingerprint=fingerprint,
                    ip_address=ip_address,
                    user_agent_hash=ua_hash,
                )
            row.ip_address = ip_address
            row.user_agent_hash = ua_hash
            self._reset_row(row, now)
            db.add(row)
            db.commit()


admin_auth_guard_service = AdminAuthGuardService()
