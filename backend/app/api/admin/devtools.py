from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from sqlalchemy import func, select

from app.core.config import settings
from app.core.security import create_access_token
from app.core.database import SessionLocal
from app.models.knowledge import KnowledgeBase
from app.models.qa_log import QALog
from app.models.task import IngestTask
from app.schemas.admin import (
    DevCheckItem,
    DevClientDebugTokenResponse,
    DevConfigResponse,
    DevConfigUpdateRequest,
    DevSelfCheckResponse,
    DevStatusResponse,
)
from app.services.config_service import ALLOWED_CONFIG_KEYS, config_service
from app.services.user_service import user_service

router = APIRouter()


@router.get("/devtools/status", response_model=DevStatusResponse)
async def devtools_status() -> DevStatusResponse:
    with SessionLocal() as db:
        kb_count = int(db.scalar(select(func.count()).select_from(KnowledgeBase)) or 0)
        doc_count = int(db.scalar(select(func.coalesce(func.sum(KnowledgeBase.doc_count), 0))) or 0)
        failed_task_count = int(
            db.scalar(
                select(func.count())
                .select_from(IngestTask)
                .where(IngestTask.status == "failed")
            )
            or 0
        )
        qa_log_count = int(db.scalar(select(func.count()).select_from(QALog)) or 0)

    return DevStatusResponse(
        app_env=settings.app_env,
        knowledge_base_count=kb_count,
        document_count=doc_count,
        failed_task_count=failed_task_count,
        qa_log_count=qa_log_count,
        qdrant_configured=bool(settings.qdrant_url),
        qa_configured=bool(settings.qa_base_url and settings.qa_api_key and settings.qa_model),
        rerank_configured=bool(settings.rerank_provider != "none" and settings.rerank_base_url and settings.rerank_model),
        wechat_configured=bool(settings.wechat_app_id and settings.wechat_app_secret),
        embedding_provider=str(settings.embedding_provider or "local_stub"),
        embedding_configured=bool(
            str(settings.embedding_provider or "local_stub").strip().lower() == "local_stub"
            or (
                settings.embedding_base_url
                and settings.embedding_api_key
                and settings.embedding_model
            )
        ),
        now_iso=datetime.now(tz=timezone.utc).isoformat(),
    )


@router.post("/devtools/self-check", response_model=DevSelfCheckResponse)
async def devtools_self_check() -> DevSelfCheckResponse:
    items: list[DevCheckItem] = []

    # DB check
    try:
        with SessionLocal() as db:
            db.scalar(select(func.count()).select_from(KnowledgeBase))
        items.append(DevCheckItem(name="database", passed=True, detail="database_ok"))
    except Exception as exc:
        items.append(DevCheckItem(name="database", passed=False, detail=f"database_error:{exc}"))

    # Uploads check
    # Keep this path consistent with app.main and upload_service.
    uploads = Path(__file__).resolve().parents[3] / "data" / "uploads"
    try:
        uploads.mkdir(parents=True, exist_ok=True)
        tmp = uploads / ".touch"
        tmp.write_text("ok", encoding="utf-8")
        tmp.unlink(missing_ok=True)
        items.append(DevCheckItem(name="uploads", passed=True, detail="uploads_writable"))
    except Exception as exc:
        items.append(DevCheckItem(name="uploads", passed=False, detail=f"uploads_error:{exc}"))

    # Config checks
    items.append(DevCheckItem(name="qa_config", passed=bool(settings.qa_base_url and settings.qa_model), detail="qa_base_url+model"))
    items.append(DevCheckItem(name="qdrant_config", passed=bool(settings.qdrant_url), detail="qdrant_url"))
    items.append(
        DevCheckItem(
            name="wechat_config",
            passed=bool(settings.wechat_app_id and settings.wechat_app_secret) or bool(settings.wechat_mock_effective),
            detail=(
                "appid+secret"
                if (settings.wechat_app_id and settings.wechat_app_secret)
                else "mock_enabled_dev_only"
            ),
        )
    )
    items.append(
        DevCheckItem(
            name="embedding_config",
            passed=bool(
                str(settings.embedding_provider or "local_stub").strip().lower() == "local_stub"
                or (settings.embedding_base_url and settings.embedding_model)
            ),
            detail=f"provider={settings.embedding_provider}",
        )
    )
    items.append(
        DevCheckItem(
            name="rerank_config",
            passed=bool(settings.rerank_provider == "none" or (settings.rerank_base_url and settings.rerank_model)),
            detail=f"provider={settings.rerank_provider}",
        )
    )

    return DevSelfCheckResponse(items=items)


@router.get("/devtools/config", response_model=DevConfigResponse)
async def devtools_get_config() -> DevConfigResponse:
    data = config_service.get_config()
    return DevConfigResponse(masked=data["masked"], editable_keys=sorted(ALLOWED_CONFIG_KEYS))


@router.post("/devtools/config", response_model=DevConfigResponse)
async def devtools_update_config(payload: DevConfigUpdateRequest) -> DevConfigResponse:
    data = config_service.update_config(payload.values)
    return DevConfigResponse(masked=data["masked"], editable_keys=sorted(ALLOWED_CONFIG_KEYS))


@router.post("/devtools/client-debug-token", response_model=DevClientDebugTokenResponse)
async def devtools_client_debug_token() -> DevClientDebugTokenResponse:
    user = user_service.get_first_active_client()
    if not user:
        raise HTTPException(status_code=404, detail="client_debug_user_not_found")

    access_token = create_access_token(
        subject=user.username,
        token_type="client",
        extra={"uid": int(user.id)},
        expire_minutes=15,
    )
    return DevClientDebugTokenResponse(
        access_token=access_token,
        user_id=int(user.id),
        username=user.username,
        display_name=user_service.get_visible_profile_name(user),
        public_name=user_service.get_public_name(user),
    )
