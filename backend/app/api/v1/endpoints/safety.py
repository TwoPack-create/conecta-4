import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.deps.auth import get_current_user
from app.schemas.common import AuthenticatedUser
from app.schemas.safety import (
    AccompanimentSessionResponse,
    MarkSafeResponse,
    StartAccompanimentRequest,
    TriggerSosRequest,
    TriggerSosResponse,
)
from app.services.safety_service import mark_accompaniment_safe, start_accompaniment_session, trigger_sos_alert

router = APIRouter(prefix="/safety", tags=["safety"])


@router.post("/accompaniment/start", response_model=AccompanimentSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_accompaniment(
    payload: StartAccompanimentRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> AccompanimentSessionResponse:
    accompaniment = await start_accompaniment_session(session, current_user, payload)
    return AccompanimentSessionResponse.model_validate(accompaniment, from_attributes=True)


@router.post("/accompaniment/{accompaniment_id}/safe", response_model=MarkSafeResponse)
async def mark_safe(
    accompaniment_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> MarkSafeResponse:
    accompaniment = await mark_accompaniment_safe(session, current_user, accompaniment_id)
    if accompaniment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Accompaniment session not found")

    return MarkSafeResponse(
        id=accompaniment.id,
        status=accompaniment.status,
        confirmed_at=accompaniment.confirmed_at,
    )


@router.post("/sos/trigger", response_model=TriggerSosResponse, status_code=status.HTTP_201_CREATED)
async def trigger_sos(
    payload: TriggerSosRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> TriggerSosResponse:
    sos_event, report, blip = await trigger_sos_alert(session, current_user, payload)
    return TriggerSosResponse(
        sos_event_id=sos_event.id,
        report_id=report.id,
        blip_id=blip.id,
        blip_expires_at=blip.expires_at,
    )
