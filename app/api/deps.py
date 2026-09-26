from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session

# Удобный алиас, чтобы в эндпоинтах писать меньше
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
