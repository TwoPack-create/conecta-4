import uuid
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ledger import WalletLedger
from app.models.participant import TripParticipant
from app.models.payment import TripPayment
from app.models.rating import TripRating
from app.models.trip import Trip
from app.models.wallet import UserWallet
from app.schemas.common import AuthenticatedUser
from app.schemas.ratings import CreateTripRatingRequest
from app.schemas.settlement import TripStatusUpdateRequest


async def request_join_trip(session: AsyncSession, current_user: AuthenticatedUser, trip_id: uuid.UUID) -> TripParticipant:
    trip = await session.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")

    existing = await session.get(TripParticipant, {"trip_id": trip_id, "user_id": current_user.id})
    if existing:
        return existing

    participant = TripParticipant(
        trip_id=trip_id,
        user_id=current_user.id,
        campus_id=current_user.campus_id,
        role="pasajero",
        status="pendiente",
    )
    session.add(participant)
    await session.commit()
    await session.refresh(participant)
    return participant


async def decide_participant(session: AsyncSession, current_user: AuthenticatedUser, trip_id: uuid.UUID, participant_id: uuid.UUID, decision: str) -> TripParticipant:
    trip = await session.get(Trip, trip_id)
    if trip is None or trip.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    participant = await session.get(TripParticipant, {"trip_id": trip_id, "user_id": participant_id})
    if participant is None:
        raise HTTPException(status_code=404, detail="Participant request not found")

    participant.status = decision
    if decision == "accepted" and trip.seats_available is not None and trip.seats_available > 0:
        trip.seats_available -= 1
    await session.commit()
    await session.refresh(participant)
    return participant


async def update_trip_status_and_settle(
    session: AsyncSession,
    current_user: AuthenticatedUser,
    trip_id: uuid.UUID,
    payload: TripStatusUpdateRequest,
) -> tuple[Trip, int, Decimal, Decimal]:
    settled_passengers = 0
    driver_credit = Decimal("0.00")
    platform_fee = Decimal("0.00")

    async with session.begin():
        result = await session.execute(select(Trip).where(Trip.id == trip_id).with_for_update())
        trip = result.scalar_one_or_none()

        if trip is None or trip.creator_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not allowed")

        if payload.status == "completado" and trip.status == "completado":
            return trip, 0, Decimal("0.00"), Decimal("0.00")

        trip.status = payload.status

        if payload.status == "completado":
            q = (
                select(TripPayment)
                .join(TripParticipant, and_(TripParticipant.trip_id == TripPayment.trip_id, TripParticipant.user_id == TripPayment.payer_user_id))
                .where(
                    TripPayment.trip_id == trip_id,
                    TripPayment.status == "retenido",
                    TripParticipant.status == "accepted",
                )
                .with_for_update()
            )
            payments = (await session.execute(q)).scalars().all()

            wallet_q = await session.execute(select(UserWallet).where(UserWallet.user_id == trip.creator_id).with_for_update())
            driver_wallet = wallet_q.scalar_one_or_none()
            if driver_wallet is None:
                raise HTTPException(status_code=400, detail="Driver wallet not found")

            for payment in payments:
                payment.status = "acreditado"
                settled_passengers += 1
                driver_credit += payment.costo_compartido
                platform_fee += payment.comision_plataforma

            driver_wallet.balance_available += driver_credit

            if driver_credit > 0:
                session.add(
                    WalletLedger(
                        id=uuid.uuid4(),
                        campus_id=current_user.campus_id,
                        user_id=trip.creator_id,
                        trip_id=trip.id,
                        entry_type="acreditacion_conductor",
                        amount=driver_credit,
                    )
                )
            if platform_fee > 0:
                session.add(
                    WalletLedger(
                        id=uuid.uuid4(),
                        campus_id=current_user.campus_id,
                        user_id=trip.creator_id,
                        trip_id=trip.id,
                        entry_type="ingreso_comision_plataforma",
                        amount=platform_fee,
                    )
                )

    await session.refresh(trip)
    return trip, settled_passengers, driver_credit, platform_fee


async def create_trip_rating(session: AsyncSession, current_user: AuthenticatedUser, payload: CreateTripRatingRequest) -> TripRating:
    trip = await session.get(Trip, payload.trip_id)
    if trip is None or trip.status != "completado":
        raise HTTPException(status_code=400, detail="Trip must be completed")

    participant = await session.get(TripParticipant, {"trip_id": payload.trip_id, "user_id": current_user.id})
    if participant is None or participant.status != "accepted":
        raise HTTPException(status_code=403, detail="Only accepted participants can rate")

    rating = TripRating(
        id=uuid.uuid4(),
        campus_id=current_user.campus_id,
        trip_id=payload.trip_id,
        rater_user_id=current_user.id,
        rated_user_id=payload.rated_user_id,
        calificacion_general=payload.calificacion_general,
        puntualidad=payload.puntualidad,
        ambiente=payload.ambiente,
        seguridad=payload.seguridad,
        comment=payload.comment,
    )
    session.add(rating)
    await session.commit()
    await session.refresh(rating)
    return rating
