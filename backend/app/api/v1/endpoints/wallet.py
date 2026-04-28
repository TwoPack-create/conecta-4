from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.deps.auth import get_current_user
from app.schemas.common import AuthenticatedUser
from app.schemas.wallet import CreateWithdrawalRequest, WalletBalanceResponse, WithdrawalRequestResponse
from app.services.wallet_service import create_withdrawal_request, get_wallet_balance

router = APIRouter(prefix="/wallet", tags=["wallet"])


@router.get("/me", response_model=WalletBalanceResponse)
async def get_my_wallet(
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> WalletBalanceResponse:
    wallet = await get_wallet_balance(session, current_user)
    if wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Wallet not found")

    return WalletBalanceResponse(
        user_id=wallet.user_id,
        campus_id=wallet.campus_id,
        balance_available=wallet.balance_available,
        balance_reserved=wallet.balance_reserved,
    )


@router.post("/withdrawals", response_model=WithdrawalRequestResponse, status_code=status.HTTP_201_CREATED)
async def create_withdrawal(
    payload: CreateWithdrawalRequest,
    current_user: AuthenticatedUser = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
) -> WithdrawalRequestResponse:
    withdrawal = await create_withdrawal_request(session, current_user, payload)
    return WithdrawalRequestResponse.model_validate(withdrawal, from_attributes=True)
