from uuid import UUID

from fastapi import APIRouter, status

from app.api.deps import SessionDep
from app.schemas.wallet import WalletInfo, WalletOperation
from app.services import wallet as wallet_service

router = APIRouter(prefix="/wallets", tags=["Кошельки"])


@router.post(
    "/",
    response_model=WalletInfo,
    status_code=status.HTTP_201_CREATED,
    summary="Создать кошелёк",
)
async def create_wallet(session: SessionDep) -> WalletInfo:
    """Создаёт новый кошелёк с нулевым балансом."""
    return await wallet_service.create_new_wallet(session)


@router.post(
    "/{wallet_uuid}/operation",
    response_model=WalletInfo,
    summary="Изменить баланс кошелька",
)
async def wallet_operation(
    wallet_uuid: UUID,
    data: WalletOperation,
    session: SessionDep,
) -> WalletInfo:
    """Пополняет или списывает средства с кошелька."""
    return await wallet_service.apply_operation(session, wallet_uuid, data)


@router.get(
    "/{wallet_uuid}",
    response_model=WalletInfo,
    summary="Получить баланс кошелька",
)
async def get_wallet(wallet_uuid: UUID, session: SessionDep) -> WalletInfo:
    """Возвращает текущий баланс кошелька."""
    return await wallet_service.get_wallet_balance(session, wallet_uuid)
