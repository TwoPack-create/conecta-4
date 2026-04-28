import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class WalletBalanceResponse(BaseModel):
    user_id: uuid.UUID
    campus_id: uuid.UUID
    balance_available: Decimal
    balance_reserved: Decimal


class CreateWithdrawalRequest(BaseModel):
    bank_account_id: uuid.UUID
    amount_requested: Decimal = Field(gt=0)


class WithdrawalRequestResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    campus_id: uuid.UUID
    bank_account_id: uuid.UUID
    amount_requested: Decimal
    status: str
    requested_at: datetime
