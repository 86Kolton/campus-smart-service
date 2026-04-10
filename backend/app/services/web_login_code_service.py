from __future__ import annotations

from datetime import datetime, timedelta, timezone
import secrets
import string

from sqlalchemy import delete, select

from app.core.database import SessionLocal
from app.models.user import User
from app.models.web_login_code import WebLoginCode


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _ensure_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _random_code(length: int = 8) -> str:
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class WebLoginCodeService:
    def _cleanup(self, db) -> None:
        now = _utcnow()
        db.execute(
            delete(WebLoginCode).where(
                (WebLoginCode.expires_at < now) | (WebLoginCode.consumed_at.is_not(None))
            )
        )

    def create_code(self, user_id: int, ttl_seconds: int = 300) -> dict:
        safe_user_id = int(user_id)
        expires_at = _utcnow() + timedelta(seconds=max(60, int(ttl_seconds or 300)))
        with SessionLocal() as db:
            self._cleanup(db)
            db.execute(delete(WebLoginCode).where(WebLoginCode.user_id == safe_user_id))
            next_id = int(db.scalar(select(WebLoginCode.id).order_by(WebLoginCode.id.desc()).limit(1)) or 0) + 1
            code = _random_code()
            while db.execute(select(WebLoginCode.id).where(WebLoginCode.code == code)).scalar_one_or_none():
                code = _random_code()
            db.add(
                WebLoginCode(
                    id=next_id,
                    user_id=safe_user_id,
                    code=code,
                    purpose="web_login",
                    expires_at=expires_at,
                    consumed_at=None,
                )
            )
            db.commit()
        return {
            "code": code,
            "expires_in": max(60, int(ttl_seconds or 300)),
            "expires_at": expires_at.isoformat(),
        }

    def consume_code(self, code: str) -> User:
        safe_code = str(code or "").strip().upper()
        if not safe_code:
            raise ValueError("web_login_code_required")

        with SessionLocal() as db:
            self._cleanup(db)
            row = db.execute(
                select(WebLoginCode).where(WebLoginCode.code == safe_code)
            ).scalar_one_or_none()
            if not row:
                raise ValueError("web_login_code_invalid")
            expires_at = _ensure_utc(row.expires_at)
            consumed_at = _ensure_utc(row.consumed_at)
            if consumed_at is not None or (expires_at is not None and expires_at < _utcnow()):
                raise ValueError("web_login_code_expired")
            user = db.get(User, int(row.user_id))
            if not user:
                raise ValueError("client_not_found")
            row.consumed_at = _utcnow()
            db.add(row)
            db.commit()
            db.refresh(user)
            return user


web_login_code_service = WebLoginCodeService()
