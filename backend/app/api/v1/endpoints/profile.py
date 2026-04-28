import uuid

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.deps.auth import get_current_user
from app.schemas.common import AuthenticatedUser
from app.schemas.profile import EmergencyContactPayload, EmergencyContactResponse
from app.services.profile_service import add_emergency_contact, delete_emergency_contact, update_emergency_contact

router = APIRouter(prefix="/profile", tags=["profile"])


@router.post("/emergency-contacts", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    payload: EmergencyContactPayload,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> EmergencyContactResponse:
    contact = await add_emergency_contact(session, current_user, payload)
    return EmergencyContactResponse.model_validate(contact, from_attributes=True)


@router.put("/emergency-contacts/{contact_id}", response_model=EmergencyContactResponse)
async def edit_contact(
    contact_id: uuid.UUID,
    payload: EmergencyContactPayload,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> EmergencyContactResponse:
    contact = await update_emergency_contact(session, current_user, contact_id, payload)
    return EmergencyContactResponse.model_validate(contact, from_attributes=True)


@router.delete("/emergency-contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_contact(
    contact_id: uuid.UUID,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> Response:
    await delete_emergency_contact(session, current_user, contact_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
