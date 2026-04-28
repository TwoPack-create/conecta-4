import uuid

from pydantic import BaseModel, Field


class EmergencyContactPayload(BaseModel):
    contact_name: str = Field(min_length=2)
    phone: str = Field(min_length=5)


class EmergencyContactResponse(BaseModel):
    id: uuid.UUID
    contact_name: str
    phone: str
