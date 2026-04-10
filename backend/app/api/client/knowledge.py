import httpx
from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import ClientIdentity, require_client_identity
from app.schemas.client import KnowledgeAskRequest, KnowledgeAskResponse
from app.services.qa_service import qa_service

router = APIRouter()


@router.post("/knowledge/ask", response_model=KnowledgeAskResponse)
async def ask_knowledge(
    payload: KnowledgeAskRequest,
    identity: ClientIdentity = Depends(require_client_identity),
) -> KnowledgeAskResponse:
    try:
        result = await qa_service.ask(
            query=payload.query,
            history=payload.history,
            kb_id=1,
            deep_thinking=payload.deep_thinking,
            user_id=identity.user_id,
        )
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=408, detail="qa_timeout") from exc
    except httpx.HTTPStatusError as exc:
        status = int(exc.response.status_code)
        if status in (401, 403):
            raise HTTPException(status_code=status, detail="qa_auth_failed") from exc
        if status >= 500:
            raise HTTPException(status_code=502, detail="qa_provider_5xx") from exc
        raise HTTPException(status_code=502, detail=f"qa_provider_http_{status}") from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="qa_pipeline_failed") from exc

    return KnowledgeAskResponse(
        answer=result["answer"],
        route=result["route"],
        route_label=result["route_label"],
        source=result["source"],
        citations=result.get("citations", []),
        related_answers=result.get("related_answers", []),
        rerank_used=bool(result.get("rerank_used", False)),
    )
