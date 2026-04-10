from __future__ import annotations

import json

from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.models.qa_log import QALog
from app.rag.pipeline import rag_pipeline


class QAService:
    async def ask(
        self,
        query: str,
        history: list[dict],
        kb_id: int = 1,
        deep_thinking: bool = False,
        user_id: int = 1,
    ) -> dict:
        result = await rag_pipeline.ask(query=query, history=history, kb_id=kb_id, deep_thinking=deep_thinking)

        with SessionLocal() as db:
            next_id = int(db.scalar(select(func.max(QALog.id))) or 0) + 1
            row = QALog(
                id=next_id,
                user_id=int(user_id),
                kb_id=kb_id,
                query_text=query,
                retrieved_chunks=json.dumps(result.get("contexts", []), ensure_ascii=False),
                rerank_used=bool(result.get("rerank_used", False)),
                answer_text=result.get("answer", ""),
                model_name=result.get("model_name", ""),
                latency_ms=int(result.get("latency_ms", 0)),
                status="success",
                error_message="",
            )
            db.add(row)
            db.commit()

        return result


qa_service = QAService()
