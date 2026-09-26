import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.wallet import Wallet


async def create_wallet(db: AsyncSession) -> Wallet:
    """Создаём новый кошелёк с нулевым балансом."""
    wallet = Wallet(balance=Decimal("0.00"))
    db.add(wallet)
    await db.commit()
    await db.refresh(wallet)
    return wallet


async def get_wallet(db: AsyncSession, wallet_id: uuid.UUID) -> Wallet | None:
    """Получаем кошелёк по id."""
    return await db.get(Wallet, wallet_id)


async def get_wallet_for_update(
    db: AsyncSession, wallet_id: uuid.UUID
) -> Wallet | None:
    """Получаем кошелёк и блокируем строку для безопасного изменения баланса.

    with_for_update() — это SELECT ... FOR UPDATE.
    Пока транзакция не завершится, никто другой не сможет изменить эту строку.
    Именно это спасает от ошибок при параллельных запросах.
    """
    result = await db.execute(
        select(Wallet).where(Wallet.id == wallet_id).with_for_update()
    )
    return result.scalar_one_or_none()
