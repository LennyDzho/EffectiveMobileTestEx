from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.database.repositories import BaseRepo


class UserRepository(BaseRepo):
    """Репозиторий для работы с таблицей users."""

    async def get_by_id(self, user_id: int) -> Optional[User]:
        stmt = select(User).where(User.id == user_id)
        return await self.session.scalar(stmt)

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        return await self.session.scalar(stmt)

    async def get_all(self, limit: int = 100, offset: int = 0) -> list[User]:
        stmt = select(User).limit(limit).offset(offset)
        result = await self.session.scalars(stmt)
        return result.all()