import uuid
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models.trip import Trip
from app.schemas.common import AuthenticatedUser
from app.schemas.trips import CreatePublicTransportTripRequest, CreateVehicleTripRequest

FUEL_EFFICIENCY_KM_PER_LITER = Decimal("8")
VARIABLE_COST_PER_KM_CLP = Decimal("80")


def _round_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def compute_vehicle_trip_costs(distance_km: Decimal, seats_total: int, settings: Settings) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    fuel_price = Decimal(str(settings.fuel_price_clp))
    platform_fee_pct = Decimal(str(settings.platform_fee_pct))

    costo_base_total = (distance_km / FUEL_EFFICIENCY_KM_PER_LITER) * fuel_price + (distance_km * VARIABLE_COST_PER_KM_CLP)
    costo_base_total = _round_money(costo_base_total)

    costo_compartido = _round_money(costo_base_total / Decimal(seats_total))
    comision_plataforma = _round_money(costo_compartido * platform_fee_pct)
    total_pasajero = _round_money(costo_compartido + comision_plataforma)

    return costo_base_total, costo_compartido, comision_plataforma, total_pasajero


async def create_vehicle_trip(
    session: AsyncSession,
    current_user: AuthenticatedUser,
    payload: CreateVehicleTripRequest,
    settings: Settings,
) -> tuple[Trip, Decimal, Decimal, Decimal, Decimal]:
    costo_base_total, costo_compartido, comision_plataforma, total_pasajero = compute_vehicle_trip_costs(
        distance_km=payload.distance_km,
        seats_total=payload.seats_total,
        settings=settings,
    )

    trip = Trip(
        id=uuid.uuid4(),
        campus_id=current_user.campus_id,
        creator_id=current_user.id,
        mode="vehiculo",
        status="publicado",
        starts_at=payload.starts_at,
        estimated_arrival_at=payload.estimated_arrival_at,
        origin_label=payload.origin_label,
        destination_label=payload.destination_label,
        origin_lat=payload.origin_lat,
        origin_lng=payload.origin_lng,
        destination_lat=payload.destination_lat,
        destination_lng=payload.destination_lng,
        route_description=payload.route_description,
        seats_total=payload.seats_total,
        seats_available=payload.seats_total,
        is_unlimited_capacity=False,
        vehicle_name=payload.vehicle_name,
        vehicle_model=payload.vehicle_model,
        vehicle_type=payload.vehicle_type,
        vehicle_color=payload.vehicle_color,
        costo_compartido=costo_compartido,
        comision_plataforma=comision_plataforma,
        acepta_encargos=payload.acepta_encargos,
    )

    session.add(trip)
    await session.commit()
    await session.refresh(trip)

    return trip, costo_base_total, costo_compartido, comision_plataforma, total_pasajero


async def create_public_transport_trip(
    session: AsyncSession,
    current_user: AuthenticatedUser,
    payload: CreatePublicTransportTripRequest,
) -> Trip:
    seats_total = None if payload.is_unlimited_capacity else payload.seats_limit
    seats_available = None if payload.is_unlimited_capacity else payload.seats_limit

    trip = Trip(
        id=uuid.uuid4(),
        campus_id=current_user.campus_id,
        creator_id=current_user.id,
        mode="transporte_publico",
        status="publicado",
        starts_at=payload.starts_at,
        estimated_arrival_at=payload.estimated_arrival_at,
        public_transport_mode=payload.transport_mode,
        line_or_route=payload.line_or_route,
        direction=payload.direction,
        origin_label=payload.origin_label,
        destination_label=payload.destination_label,
        origin_lat=payload.origin_lat,
        origin_lng=payload.origin_lng,
        destination_lat=payload.destination_lat,
        destination_lng=payload.destination_lng,
        route_description=payload.route_description,
        seats_total=seats_total,
        seats_available=seats_available,
        is_unlimited_capacity=payload.is_unlimited_capacity,
        costo_compartido=Decimal("0.00"),
        comision_plataforma=Decimal("0.00"),
        acepta_encargos=False,
    )

    session.add(trip)
    await session.commit()
    await session.refresh(trip)
    return trip
