from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select, update

from app.core.database import SessionLocal
from app.models.refresh_token import RefreshToken
from app.models.token_revocation import TokenRevocation


def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def _to_utc_aware(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return None
        text = text.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(text)
        except ValueError:
            return None
        value = parsed
    if not isinstance(value, datetime):
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


class TokenService:
    def store_refresh_token(self, user_id: int, jti: str, expires_at: datetime) -> None:
        with SessionLocal() as db:
            next_id = int(db.scalar(select(RefreshToken.id).order_by(RefreshToken.id.desc()).limit(1)) or 0) + 1
            db.add(
                RefreshToken(
                    id=next_id,
                    user_id=int(user_id),
                    jti=str(jti),
                    revoked=False,
                    expires_at=expires_at,
                )
            )
            db.commit()

    def revoke_refresh_token(self, jti: str) -> None:
        with SessionLocal() as db:
            db.execute(
                update(RefreshToken)
                .where(RefreshToken.jti == str(jti))
                .values(revoked=True)
            )
            db.commit()

    def revoke_all_refresh_tokens(self, user_id: int) -> None:
        with SessionLocal() as db:
            db.execute(
                update(RefreshToken)
                .where(RefreshToken.user_id == int(user_id))
                .values(revoked=True)
            )
            db.commit()

    def is_refresh_token_valid(self, jti: str, user_id: int) -> bool:
        with SessionLocal() as db:
            row = db.execute(
                select(RefreshToken)
                .where(
                    RefreshToken.jti == str(jti),
                    RefreshToken.user_id == int(user_id),
                )
            ).scalar_one_or_none()
            if not row or row.revoked:
                return False
            expires_at = _to_utc_aware(row.expires_at)
            if expires_at and expires_at < _utcnow():
                return False
            return True

    def revoke_access_token(self, jti: str, token_type: str, expires_at: datetime) -> None:
        with SessionLocal() as db:
            exists = db.execute(
                select(TokenRevocation)
                .where(TokenRevocation.jti == str(jti))
            ).scalar_one_or_none()
            if exists:
                return
            next_id = int(db.scalar(select(TokenRevocation.id).order_by(TokenRevocation.id.desc()).limit(1)) or 0) + 1
            db.add(
                TokenRevocation(
                    id=next_id,
                    jti=str(jti),
                    token_type=str(token_type),
                    expires_at=expires_at,
                )
            )
            db.commit()

    def is_token_revoked(self, jti: str) -> bool:
        with SessionLocal() as db:
            row = db.execute(
                select(TokenRevocation)
                .where(TokenRevocation.jti == str(jti))
            ).scalar_one_or_none()
            if not row:
                return False
            expires_at = _to_utc_aware(row.expires_at)
            if expires_at and expires_at < _utcnow():
                return False
            return True


token_service = TokenService()
