from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import UserWallet, WithdrawalRequest
from app.schemas.common import AuthenticatedUser
from app.schemas.wallet import CreateWithdrawalRequest


async def get_wallet_balance(session: AsyncSession, current_user: AuthenticatedUser) -> UserWallet | None:
    result = await session.execute(
        select(UserWallet).where(
            UserWallet.user_id == current_user.id,
            UserWallet.campus_id == current_user.campus_id,
        )
    )
    return result.scalar_one_or_none()


async def create_withdrawal_request(
    session: AsyncSession,
    current_user: AuthenticatedUser,
    payload: CreateWithdrawalRequest,
) -> WithdrawalRequest:
    withdrawal = WithdrawalRequest(
        user_id=current_user.id,
        campus_id=current_user.campus_id,
        bank_account_id=payload.bank_account_id,
        amount_requested=payload.amount_requested,
        status="solicitado",
    )
    session.add(withdrawal)
    await session.commit()
    await session.refresh(withdrawal)
    return withdrawal
