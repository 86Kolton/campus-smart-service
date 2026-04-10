from fastapi import APIRouter, Depends

from app.api.admin import auth, dashboard, devtools, documents, evolution, kb, logs, maintenance, moderation, tasks
from app.api.deps import require_admin_token
from app.api.client import auth as client_auth
from app.api.client import edu, errand, feed, knowledge, messages, profile, search

api_router = APIRouter()

client_router = APIRouter(prefix="/api/client")
client_router.include_router(client_auth.router, tags=["client-auth"])
client_router.include_router(feed.router, tags=["client-feed"])
client_router.include_router(search.router, tags=["client-search"])
client_router.include_router(messages.router, tags=["client-messages"])
client_router.include_router(profile.router, tags=["client-profile"])
client_router.include_router(knowledge.router, tags=["client-knowledge"])
client_router.include_router(edu.router, tags=["client-edu"])
client_router.include_router(errand.router, tags=["client-errand"])

admin_router = APIRouter(prefix="/api/admin")
admin_router.include_router(auth.router, tags=["admin-auth"])
admin_router.include_router(dashboard.router, tags=["admin-dashboard"], dependencies=[Depends(require_admin_token)])
admin_router.include_router(kb.router, tags=["admin-kb"], dependencies=[Depends(require_admin_token)])
admin_router.include_router(documents.router, tags=["admin-documents"], dependencies=[Depends(require_admin_token)])
admin_router.include_router(tasks.router, tags=["admin-tasks"], dependencies=[Depends(require_admin_token)])
admin_router.include_router(logs.router, tags=["admin-logs"], dependencies=[Depends(require_admin_token)])
admin_router.include_router(evolution.router, tags=["admin-rag-evolution"], dependencies=[Depends(require_admin_token)])
admin_router.include_router(moderation.router, tags=["admin-moderation"], dependencies=[Depends(require_admin_token)])
admin_router.include_router(maintenance.router, tags=["admin-maintenance"], dependencies=[Depends(require_admin_token)])
admin_router.include_router(devtools.router, tags=["admin-devtools"], dependencies=[Depends(require_admin_token)])

api_router.include_router(client_router)
api_router.include_router(admin_router)
