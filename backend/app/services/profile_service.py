import uuid

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import EmergencyContact
from app.schemas.common import AuthenticatedUser
from app.schemas.profile import EmergencyContactPayload


async def add_emergency_contact(session: AsyncSession, current_user: AuthenticatedUser, payload: EmergencyContactPayload) -> EmergencyContact:
    count_q = await session.execute(select(func.count()).select_from(EmergencyContact).where(EmergencyContact.user_id == current_user.id))
    if (count_q.scalar() or 0) >= 3:
        raise HTTPException(status_code=400, detail="Maximum 3 emergency contacts")

    contact = EmergencyContact(
        id=uuid.uuid4(),
        user_id=current_user.id,
        campus_id=current_user.campus_id,
        contact_name=payload.contact_name,
        phone=payload.phone,
    )
    session.add(contact)
    await session.commit()
    await session.refresh(contact)
    return contact


async def update_emergency_contact(
    session: AsyncSession,
    current_user: AuthenticatedUser,
    contact_id: uuid.UUID,
    payload: EmergencyContactPayload,
) -> EmergencyContact:
    contact = await session.get(EmergencyContact, contact_id)
    if contact is None or contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    contact.contact_name = payload.contact_name
    contact.phone = payload.phone
    await session.commit()
    await session.refresh(contact)
    return contact


async def delete_emergency_contact(session: AsyncSession, current_user: AuthenticatedUser, contact_id: uuid.UUID) -> None:
    contact = await session.get(EmergencyContact, contact_id)
    if contact is None or contact.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contact not found")
    await session.delete(contact)
    await session.commit()
