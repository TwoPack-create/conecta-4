import uuid

from pydantic import BaseModel, Field


class CreateTripRatingRequest(BaseModel):
    trip_id: uuid.UUID
    rated_user_id: uuid.UUID
    calificacion_general: int = Field(ge=1, le=5)
    puntualidad: int = Field(ge=1, le=5)
    ambiente: int = Field(ge=1, le=5)
    seguridad: int = Field(ge=1, le=5)
    comment: str | None = None


class TripRatingResponse(BaseModel):
    id: uuid.UUID
    trip_id: uuid.UUID
    rater_user_id: uuid.UUID
    rated_user_id: uuid.UUID
