import uuid

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.route import ReportVote, RouteReport
from app.schemas.common import AuthenticatedUser
from app.schemas.routes import CreateRouteReportRequest


async def create_route_report(session: AsyncSession, current_user: AuthenticatedUser, payload: CreateRouteReportRequest) -> RouteReport:
    report = RouteReport(
        id=uuid.uuid4(),
        campus_id=current_user.campus_id,
        created_by=current_user.id,
        report_type=payload.tipo_reporte,
        risk_level=payload.nivel_riesgo,
        location_label=payload.ubicacion,
        description=payload.descripcion,
        lat=payload.lat,
        lng=payload.lng,
    )
    session.add(report)
    await session.commit()
    await session.refresh(report)
    return report


async def vote_route_report(session: AsyncSession, current_user: AuthenticatedUser, report_id: uuid.UUID, vote: int) -> ReportVote:
    report = await session.get(RouteReport, report_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    existing = await session.get(ReportVote, {"report_id": report_id, "voter_user_id": current_user.id})
    if existing:
        existing.vote = vote
        await session.commit()
        await session.refresh(existing)
        return existing

    rv = ReportVote(
        report_id=report_id,
        voter_user_id=current_user.id,
        campus_id=current_user.campus_id,
        vote=vote,
    )
    session.add(rv)
    await session.commit()
    await session.refresh(rv)
    return rv
