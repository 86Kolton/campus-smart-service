import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.api.router import api_router
from app.core.config import settings
from app.services.bootstrap_service import bootstrap_database
from app.services.evolution_realtime_service import evolution_realtime_service
from app.services.knowledge_cache_service import knowledge_cache_service
from app.services.maintenance_service import maintenance_service


@asynccontextmanager
async def app_lifespan(_app: FastAPI):
    bootstrap_database()
    knowledge_cache_service.rebuild_chunks()
    try:
        maintenance_service.cleanup_stale_unadopted_posts(days=7)
    except Exception:
        # Do not block startup if cleanup fails.
        pass
    evolution_realtime_service.request_sync(reason="startup")

    async def periodic_cleanup() -> None:
        while True:
            try:
                maintenance_service.cleanup_stale_unadopted_posts(days=7)
            except Exception:
                pass
            await asyncio.sleep(6 * 60 * 60)

    async def periodic_evolution_sync() -> None:
        while True:
            evolution_realtime_service.request_sync(reason="periodic")
            await asyncio.sleep(10 * 60)

    cleanup_task = asyncio.create_task(periodic_cleanup())
    evolution_task = asyncio.create_task(periodic_evolution_sync())
    try:
        yield
    finally:
        if cleanup_task and not cleanup_task.done():
            cleanup_task.cancel()
            try:
                await cleanup_task
            except BaseException:
                pass
        if evolution_task and not evolution_task.done():
            evolution_task.cancel()
            try:
                await evolution_task
            except BaseException:
                pass


def create_app() -> FastAPI:
    if settings.startup_issues:
        raise RuntimeError("; ".join(settings.startup_issues))
    app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=app_lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router)
    uploads_dir = Path(__file__).resolve().parents[1] / "data" / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")
    studio_dir = Path(__file__).resolve().parent / "static" / "studio"
    studio_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/studio", StaticFiles(directory=str(studio_dir), html=True), name="studio")

    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/studio/", status_code=302)

    @app.get("/healthz", tags=["health"])
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
