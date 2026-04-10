from sqlalchemy import func, select

from fastapi import APIRouter

from app.core.database import SessionLocal
from app.models.knowledge import KnowledgeBase
from app.models.qa_log import QALog
from app.models.task import IngestTask
from app.schemas.admin import DashboardResponse

router = APIRouter()


@router.get("/dashboard/summary", response_model=DashboardResponse)
async def dashboard_summary() -> DashboardResponse:
    with SessionLocal() as db:
        kb_count = int(db.scalar(select(func.count()).select_from(KnowledgeBase)) or 0)
        doc_count = int(db.scalar(select(func.coalesce(func.sum(KnowledgeBase.doc_count), 0))) or 0)
        chunk_count = int(db.scalar(select(func.coalesce(func.sum(KnowledgeBase.chunk_count), 0))) or 0)
        failed_tasks = int(
            db.scalar(
                select(func.count()).select_from(IngestTask).where(IngestTask.status == "failed")
            )
            or 0
        )
        qa_count = int(db.scalar(select(func.count()).select_from(QALog)) or 0)

    return DashboardResponse(
        knowledge_base_count=kb_count,
        document_count=doc_count,
        chunk_count=chunk_count,
        today_qa_count=qa_count,
        failed_task_count=failed_tasks,
    )
