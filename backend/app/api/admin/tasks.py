from fastapi import APIRouter

from app.schemas.admin import IngestTaskItem, IngestTaskListResponse
from app.schemas.common import MessageResponse
from app.services.task_service import task_service

router = APIRouter()


@router.get("/tasks", response_model=IngestTaskListResponse)
async def list_tasks() -> IngestTaskListResponse:
    return IngestTaskListResponse(items=[IngestTaskItem(**row) for row in task_service.list_tasks()])


@router.post("/tasks/{task_id}/retry", response_model=MessageResponse)
async def retry_task(task_id: int) -> MessageResponse:
    task = task_service.retry_task(task_id)
    if not task:
        return MessageResponse(message="not_found")
    return MessageResponse(message=f"task_id={task_id} status={task['status']}")
