import uuid
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class CreateVehicleTripRequest(BaseModel):
    starts_at: datetime
    estimated_arrival_at: datetime | None = None

    origin_label: str = Field(min_length=3)
    destination_label: str = Field(min_length=3)
    origin_lat: Decimal | None = None
    origin_lng: Decimal | None = None
    destination_lat: Decimal | None = None
    destination_lng: Decimal | None = None

    distance_km: Decimal = Field(gt=0)
    seats_total: int = Field(ge=3)

    vehicle_name: str | None = None
    vehicle_model: str | None = None
    vehicle_type: str | None = None
    vehicle_color: str | None = None

    route_description: str | None = None
    acepta_encargos: bool = False


class CreatePublicTransportTripRequest(BaseModel):
    starts_at: datetime
    estimated_arrival_at: datetime | None = None

    transport_mode: Literal["metro", "micro", "a_pie"]
    line_or_route: str | None = None
    direction: str | None = None

    origin_label: str = Field(min_length=3)
    destination_label: str = Field(min_length=3)
    origin_lat: Decimal | None = None
    origin_lng: Decimal | None = None
    destination_lat: Decimal | None = None
    destination_lng: Decimal | None = None

    route_description: str | None = None
    is_unlimited_capacity: bool = False
    seats_limit: int | None = Field(default=None, ge=3)

    @model_validator(mode="after")
    def validate_capacity(self) -> "CreatePublicTransportTripRequest":
        if self.is_unlimited_capacity and self.seats_limit is not None:
            raise ValueError("Si el viaje es ilimitado, seats_limit debe ser null")
        if not self.is_unlimited_capacity and self.seats_limit is None:
            raise ValueError("Si el viaje no es ilimitado, seats_limit es obligatorio")
        return self


class VehicleTripCostBreakdown(BaseModel):
    costo_base_total: Decimal
    costo_compartido: Decimal
    comision_plataforma: Decimal
    total_pasajero: Decimal


class TripCreatedResponse(BaseModel):
    id: uuid.UUID
    campus_id: uuid.UUID
    creator_id: uuid.UUID
    mode: str
    status: str
    starts_at: datetime
    origin_label: str
    destination_label: str
    seats_total: int | None
    seats_available: int | None
    is_unlimited_capacity: bool
    public_transport_mode: str | None = None
    line_or_route: str | None = None
    direction: str | None = None
    acepta_encargos: bool
    costo: VehicleTripCostBreakdown | None = None
