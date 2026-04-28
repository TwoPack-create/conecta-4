from sqlalchemy.ext.asyncio import AsyncSession

from app.models.payment import TripPayment
from app.schemas.common import AuthenticatedUser
from app.schemas.payments import SimulateRetainedPaymentRequest


async def create_retained_payment(
    session: AsyncSession,
    current_user: AuthenticatedUser,
    payload: SimulateRetainedPaymentRequest,
) -> TripPayment:
    payment = TripPayment(
        campus_id=current_user.campus_id,
        trip_id=payload.trip_id,
        payer_user_id=current_user.id,
        driver_user_id=payload.driver_user_id,
        amount_total=payload.amount_total,
        costo_compartido=payload.costo_compartido,
        comision_plataforma=payload.comision_plataforma,
        status="retenido",
    )
    session.add(payment)
    await session.commit()
    await session.refresh(payment)
    return payment
