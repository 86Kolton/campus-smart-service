from sqlalchemy import select

from fastapi import APIRouter

from app.core.database import SessionLocal
from app.models.qa_log import QALog
from app.schemas.admin import QALogItem, QALogListResponse

router = APIRouter()


@router.get("/logs/qa", response_model=QALogListResponse)
async def list_qa_logs() -> QALogListResponse:
    with SessionLocal() as db:
        rows = db.execute(select(QALog).order_by(QALog.id.desc()).limit(200)).scalars().all()

    items = [
        QALogItem(
            id=int(row.id),
            query_text=row.query_text,
            answer_text=row.answer_text,
            model_name=row.model_name,
            latency_ms=int(row.latency_ms or 0),
            status=row.status,
            created_at=row.created_at.isoformat() if row.created_at else "",
        )
        for row in rows
    ]
    return QALogListResponse(items=items)

