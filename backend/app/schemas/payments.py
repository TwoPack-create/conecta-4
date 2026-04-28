import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator


class SimulateRetainedPaymentRequest(BaseModel):
    trip_id: uuid.UUID
    driver_user_id: uuid.UUID
    amount_total: Decimal = Field(ge=0)
    costo_compartido: Decimal = Field(ge=0)
    comision_plataforma: Decimal = Field(ge=0)
    gateway_provider: str | None = None
    gateway_payment_id: str | None = None

    @model_validator(mode="after")
    def validate_split(self) -> "SimulateRetainedPaymentRequest":
        if self.amount_total != self.costo_compartido + self.comision_plataforma:
            raise ValueError("amount_total debe ser igual a costo_compartido + comision_plataforma")
        return self


class TripPaymentResponse(BaseModel):
    id: uuid.UUID
    campus_id: uuid.UUID
    trip_id: uuid.UUID
    payer_user_id: uuid.UUID
    driver_user_id: uuid.UUID
    amount_total: Decimal
    costo_compartido: Decimal
    comision_plataforma: Decimal
    status: str
    retained_at: datetime
