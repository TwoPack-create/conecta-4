import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class StartAccompanimentRequest(BaseModel):
    estimated_minutes: int = Field(ge=1, le=720)
    last_lat: Decimal | None = None
    last_lng: Decimal | None = None


class AccompanimentSessionResponse(BaseModel):
    id: uuid.UUID
    status: str
    expected_arrival_at: datetime
    started_at: datetime


class MarkSafeResponse(BaseModel):
    id: uuid.UUID
    status: str
    confirmed_at: datetime


class TriggerSosRequest(BaseModel):
    location_label: str = Field(min_length=3)
    lat: Decimal
    lng: Decimal
    description: str = Field(min_length=3)


class TriggerSosResponse(BaseModel):
    sos_event_id: uuid.UUID
    report_id: uuid.UUID
    blip_id: uuid.UUID
    blip_expires_at: datetime
