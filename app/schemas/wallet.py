import uuid
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class OperationType(str, Enum):
    """Тип операции: пополнение или списание."""

    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"


class WalletOperation(BaseModel):
    """Тело запроса на изменение баланса."""
    operation_type: OperationType
    amount: Decimal = Field(gt=0, description="Сумма должна быть больше нуля")


class WalletInfo(BaseModel):
    """Ответ с информацией о кошельке."""
    id: uuid.UUID
    balance: Decimal

    model_config = ConfigDict(from_attributes=True)
