import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.deps.auth import get_current_user
from app.schemas.common import AuthenticatedUser
from app.schemas.participation import JoinTripRequest, ParticipantDecisionRequest, ParticipantResponse
from app.schemas.ratings import CreateTripRatingRequest, TripRatingResponse
from app.schemas.settlement import TripStatusUpdateRequest, TripStatusUpdateResponse
from app.services.participation_service import (
    create_trip_rating,
    decide_participant,
    request_join_trip,
    update_trip_status_and_settle,
)

router = APIRouter(prefix="/participation", tags=["participation"])


@router.post("/join", response_model=ParticipantResponse, status_code=status.HTTP_201_CREATED)
async def join_trip(
    payload: JoinTripRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ParticipantResponse:
    participant = await request_join_trip(session, current_user, payload.trip_id)
    return ParticipantResponse.model_validate(participant, from_attributes=True)


@router.post("/trips/{trip_id}/participants/{participant_id}/decision", response_model=ParticipantResponse)
async def participant_decision(
    trip_id: uuid.UUID,
    participant_id: uuid.UUID,
    payload: ParticipantDecisionRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> ParticipantResponse:
    participant = await decide_participant(session, current_user, trip_id, participant_id, payload.decision)
    return ParticipantResponse.model_validate(participant, from_attributes=True)


@router.post("/trips/{trip_id}/status", response_model=TripStatusUpdateResponse)
async def update_trip_status(
    trip_id: uuid.UUID,
    payload: TripStatusUpdateRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> TripStatusUpdateResponse:
    trip, settled_passengers, total_driver_credit, total_platform_fee = await update_trip_status_and_settle(
        session,
        current_user,
        trip_id,
        payload,
    )
    return TripStatusUpdateResponse(
        trip_id=trip.id,
        status=trip.status,
        settled_passengers=settled_passengers,
        total_driver_credit=total_driver_credit,
        total_platform_fee=total_platform_fee,
    )


@router.post("/ratings", response_model=TripRatingResponse, status_code=status.HTTP_201_CREATED)
async def rate_trip(
    payload: CreateTripRatingRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> TripRatingResponse:
    rating = await create_trip_rating(session, current_user, payload)
    return TripRatingResponse.model_validate(rating, from_attributes=True)
