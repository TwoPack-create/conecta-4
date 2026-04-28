import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.deps.auth import get_current_user
from app.schemas.common import AuthenticatedUser
from app.schemas.routes import (
    CreateRouteReportRequest,
    RouteReportResponse,
    VoteRouteReportRequest,
    VoteRouteReportResponse,
)
from app.services.routes_service import create_route_report, vote_route_report

router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/reports", response_model=RouteReportResponse, status_code=status.HTTP_201_CREATED)
async def publish_route_report(
    payload: CreateRouteReportRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> RouteReportResponse:
    report = await create_route_report(session, current_user, payload)
    return RouteReportResponse(
        id=report.id,
        tipo_reporte=report.report_type,
        nivel_riesgo=report.risk_level,
        ubicacion=report.location_label,
        descripcion=report.description,
        created_at=report.created_at,
    )


@router.post("/reports/{report_id}/vote", response_model=VoteRouteReportResponse)
async def vote_report(
    report_id: uuid.UUID,
    payload: VoteRouteReportRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> VoteRouteReportResponse:
    vote = await vote_route_report(session, current_user, report_id, payload.vote)
    return VoteRouteReportResponse(report_id=vote.report_id, voter_user_id=vote.voter_user_id, vote=vote.vote)
