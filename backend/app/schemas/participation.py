import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class JoinTripRequest(BaseModel):
    trip_id: uuid.UUID


class ParticipantDecisionRequest(BaseModel):
    decision: Literal["accepted", "rejected"]


class ParticipantResponse(BaseModel):
    trip_id: uuid.UUID
    user_id: uuid.UUID
    status: str
    joined_at: datetime
