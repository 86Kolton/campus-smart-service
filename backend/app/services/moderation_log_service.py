from __future__ import annotations

import json
from datetime import datetime, timezone

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.moderation_log import ModerationLog


class ModerationLogService:
    def add(self, action: str, actor_id: int, target_type: str, target_id: str, detail: dict | None = None) -> None:
        payload = json.dumps(detail or {}, ensure_ascii=False)
        with SessionLocal() as db:
            next_id = int(db.scalar(select(func.max(ModerationLog.id))) or 0) + 1
            row = ModerationLog(
                id=next_id,
                action=action,
                actor_id=int(actor_id),
                target_type=target_type,
                target_id=str(target_id),
                detail=payload,
                created_at=datetime.now(tz=timezone.utc),
            )
            db.add(row)
            db.commit()

    def list_latest(self, limit: int = 200) -> list[ModerationLog]:
        with SessionLocal() as db:
            return db.execute(select(ModerationLog).order_by(ModerationLog.id.desc()).limit(limit)).scalars().all()


moderation_log_service = ModerationLogService()
