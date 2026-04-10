from fastapi import APIRouter, Depends, Header, HTTPException, Query

from app.api.deps import ClientIdentity, require_client_identity
from app.schemas.client import (
    EduExamListResponse,
    EduFreeClassroomResponse,
    EduGradeListResponse,
    EduOverviewResponse,
    EduScheduleResponse,
)
from app.services.edu_service import edu_service

router = APIRouter()


def require_edu_session(
    identity: ClientIdentity = Depends(require_client_identity),
    edu_session: str | None = Header(default=None, alias="X-Edu-Session"),
) -> ClientIdentity:
    if not str(edu_session or "").strip():
        raise HTTPException(status_code=401, detail="edu_session_required")
    return identity


@router.get("/edu/overview", response_model=EduOverviewResponse)
async def edu_overview(identity: ClientIdentity = Depends(require_edu_session)) -> EduOverviewResponse:
    del identity
    return EduOverviewResponse(**edu_service.overview())


@router.get("/edu/grades", response_model=EduGradeListResponse)
async def edu_grades(
    term: str | None = Query(default=None),
    identity: ClientIdentity = Depends(require_edu_session),
) -> EduGradeListResponse:
    del identity
    return EduGradeListResponse(**edu_service.grades(term=term))


@router.get("/edu/exams", response_model=EduExamListResponse)
async def edu_exams(identity: ClientIdentity = Depends(require_edu_session)) -> EduExamListResponse:
    del identity
    return EduExamListResponse(**edu_service.exams())


@router.get("/edu/schedule", response_model=EduScheduleResponse)
async def edu_schedule(
    week_no: int = Query(default=1, ge=1, le=18),
    identity: ClientIdentity = Depends(require_edu_session),
) -> EduScheduleResponse:
    del identity
    return EduScheduleResponse(**edu_service.schedule(week_no=week_no))


@router.get("/edu/free-classrooms", response_model=EduFreeClassroomResponse)
async def edu_free_classrooms(
    campus: str = Query(default="七一路校区"),
    building: str | None = Query(default=None),
    identity: ClientIdentity = Depends(require_edu_session),
) -> EduFreeClassroomResponse:
    del identity
    return EduFreeClassroomResponse(**edu_service.free_classrooms(campus=campus, building=building))
