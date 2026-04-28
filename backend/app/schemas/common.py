import uuid

from pydantic import BaseModel


class AuthenticatedUser(BaseModel):
    id: uuid.UUID
    campus_id: uuid.UUID
    is_admin: bool = False
