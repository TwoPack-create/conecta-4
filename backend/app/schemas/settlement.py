import uuid
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class TripStatusUpdateRequest(BaseModel):
    status: Literal["en_curso", "completado"]


class TripStatusUpdateResponse(BaseModel):
    trip_id: uuid.UUID
    status: str
    settled_passengers: int = 0
    total_driver_credit: Decimal = Field(default=Decimal("0.00"))
    total_platform_fee: Decimal = Field(default=Decimal("0.00"))
