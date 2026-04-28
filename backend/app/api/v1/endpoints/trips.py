from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_db_session
from app.deps.auth import get_current_user
from app.schemas.common import AuthenticatedUser
from app.schemas.trips import (
    CreatePublicTransportTripRequest,
    CreateVehicleTripRequest,
    TripCreatedResponse,
    VehicleTripCostBreakdown,
)
from app.services.trip_service import create_public_transport_trip, create_vehicle_trip

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("/vehicle", response_model=TripCreatedResponse, status_code=status.HTTP_201_CREATED)
async def publish_vehicle_trip(
    payload: CreateVehicleTripRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    settings: Settings = Depends(get_settings),
) -> TripCreatedResponse:
    trip, costo_base_total, costo_compartido, comision_plataforma, total_pasajero = await create_vehicle_trip(
        session=session,
        current_user=current_user,
        payload=payload,
        settings=settings,
    )

    return TripCreatedResponse(
        id=trip.id,
        campus_id=trip.campus_id,
        creator_id=trip.creator_id,
        mode=trip.mode,
        status=trip.status,
        starts_at=trip.starts_at,
        origin_label=trip.origin_label,
        destination_label=trip.destination_label,
        seats_total=trip.seats_total,
        seats_available=trip.seats_available,
        is_unlimited_capacity=trip.is_unlimited_capacity,
        acepta_encargos=trip.acepta_encargos,
        costo=VehicleTripCostBreakdown(
            costo_base_total=costo_base_total,
            costo_compartido=costo_compartido,
            comision_plataforma=comision_plataforma,
            total_pasajero=total_pasajero,
        ),
    )


@router.post("/public-transport", response_model=TripCreatedResponse, status_code=status.HTTP_201_CREATED)
async def publish_public_transport_trip(
    payload: CreatePublicTransportTripRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> TripCreatedResponse:
    trip = await create_public_transport_trip(session=session, current_user=current_user, payload=payload)
    return TripCreatedResponse(
        id=trip.id,
        campus_id=trip.campus_id,
        creator_id=trip.creator_id,
        mode=trip.mode,
        status=trip.status,
        starts_at=trip.starts_at,
        origin_label=trip.origin_label,
        destination_label=trip.destination_label,
        seats_total=trip.seats_total,
        seats_available=trip.seats_available,
        is_unlimited_capacity=trip.is_unlimited_capacity,
        public_transport_mode=trip.public_transport_mode,
        line_or_route=trip.line_or_route,
        direction=trip.direction,
        acepta_encargos=trip.acepta_encargos,
        costo=None,
    )
