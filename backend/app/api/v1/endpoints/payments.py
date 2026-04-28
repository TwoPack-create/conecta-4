from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.deps.auth import get_current_user
from app.schemas.common import AuthenticatedUser
from app.schemas.payments import SimulateRetainedPaymentRequest, TripPaymentResponse
from app.services.payment_service import create_retained_payment

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/simulate-retained", response_model=TripPaymentResponse, status_code=status.HTTP_201_CREATED)
async def simulate_retained_payment(
    payload: SimulateRetainedPaymentRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> TripPaymentResponse:
    payment = await create_retained_payment(session, current_user, payload)
    return TripPaymentResponse.model_validate(payment, from_attributes=True)
