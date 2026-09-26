import uuid

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import wallet as wallet_crud
from app.models.wallet import Wallet
from app.schemas.wallet import OperationType, WalletOperation


async def create_new_wallet(db: AsyncSession) -> Wallet:
    """Создаём кошелёк (для тестов и старта)."""
    return await wallet_crud.create_wallet(db)


async def get_wallet_balance(db: AsyncSession, wallet_id: uuid.UUID) -> Wallet:
    """Отдаём кошелёк или 404."""
    wallet = await wallet_crud.get_wallet(db, wallet_id)
    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кошелёк не найден",
        )
    return wallet


async def apply_operation(
    db: AsyncSession, wallet_id: uuid.UUID, data: WalletOperation
) -> Wallet:
    """Пополнение или списание средств.

    Используем блокировку строки (with_for_update), чтобы два
    параллельных запроса к одному кошельку не перезаписали баланс.
    """
    wallet = await wallet_crud.get_wallet_for_update(db, wallet_id)
    if wallet is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Кошелёк не найден",
        )

    if data.operation_type == OperationType.DEPOSIT:
        wallet.balance = wallet.balance + data.amount
    else:
        if wallet.balance < data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недостаточно средств",
            )
        wallet.balance = wallet.balance - data.amount

    await db.commit()
    await db.refresh(wallet)
    return wallet
