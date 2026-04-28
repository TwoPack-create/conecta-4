import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.safety import AccompanimentSession, Blip, RouteReport, SosEvent
from app.schemas.common import AuthenticatedUser
from app.schemas.safety import StartAccompanimentRequest, TriggerSosRequest


async def start_accompaniment_session(
    session: AsyncSession,
    current_user: AuthenticatedUser,
    payload: StartAccompanimentRequest,
) -> AccompanimentSession:
    now = datetime.now(UTC)
    accompaniment = AccompanimentSession(
        id=uuid.uuid4(),
        campus_id=current_user.campus_id,
        user_id=current_user.id,
        status="activo",
        target_type="contactos_externos",
        expected_arrival_at=now + timedelta(minutes=payload.estimated_minutes),
        started_at=now,
        created_at=now,
        updated_at=now,
        last_lat=payload.last_lat,
        last_lng=payload.last_lng,
    )
    session.add(accompaniment)
    await session.commit()
    await session.refresh(accompaniment)
    return accompaniment


async def mark_accompaniment_safe(
    session: AsyncSession,
    current_user: AuthenticatedUser,
    accompaniment_id: uuid.UUID,
) -> AccompanimentSession | None:
    result = await session.execute(
        select(AccompanimentSession).where(
            AccompanimentSession.id == accompaniment_id,
            AccompanimentSession.user_id == current_user.id,
            AccompanimentSession.campus_id == current_user.campus_id,
        )
    )
    accompaniment = result.scalar_one_or_none()
    if accompaniment is None:
        return None

    now = datetime.now(UTC)
    accompaniment.status = "confirmado"
    accompaniment.confirmed_at = now
    accompaniment.updated_at = now
    await session.commit()
    await session.refresh(accompaniment)
    return accompaniment


async def trigger_sos_alert(
    session: AsyncSession,
    current_user: AuthenticatedUser,
    payload: TriggerSosRequest,
) -> tuple[SosEvent, RouteReport, Blip]:
    now = datetime.now(UTC)

    sos_event = SosEvent(
        id=uuid.uuid4(),
        campus_id=current_user.campus_id,
        user_id=current_user.id,
        event_type="sos_manual",
        lat=payload.lat,
        lng=payload.lng,
        created_at=now,
    )

    report = RouteReport(
        id=uuid.uuid4(),
        campus_id=current_user.campus_id,
        created_by=current_user.id,
        report_type="incidente",
        risk_level="alto",
        location_label=payload.location_label,
        lat=payload.lat,
        lng=payload.lng,
        incident_at=now,
        description=payload.description,
        created_at=now,
    )

    blip = Blip(
        id=uuid.uuid4(),
        campus_id=current_user.campus_id,
        created_by=current_user.id,
        report_id=report.id,
        lat=payload.lat,
        lng=payload.lng,
        message=payload.description,
        is_high_priority=True,
        created_at=now,
        expires_at=now + timedelta(hours=24),
    )

    session.add_all([sos_event, report, blip])
    await session.commit()
    return sos_event, report, blip


async def detonate_expired_accompaniment_sessions(session: AsyncSession) -> int:
    now = datetime.now(UTC)
    result = await session.execute(
        update(AccompanimentSession)
        .where(
            AccompanimentSession.status == "activo",
            AccompanimentSession.expected_arrival_at < now,
        )
        .values(status="alerta_detonada", expired_at=now, updated_at=now)
    )
    await session.commit()
    return result.rowcount or 0
