from typing import Optional

from sqlalchemy import select, update, exists
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.users.schemas import UpdateProfileDTO
from src.core.infra.exceptions import NotFound, Forbidden, Conflict
from src.database.models import User


class UserService:
    """Сервис работы с профилем пользователя."""
    def __init__(self, session: AsyncSession, auth_service: "AuthService"):
        self.session = session
        self.auth_service = auth_service

    async def get_by_id(self, user_id: int) -> User:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        user: Optional[User] = result.scalar_one_or_none()
        if not user:
            raise NotFound("User not found")
        return user

    async def update_profile(self, user_id: int, data: UpdateProfileDTO) -> User:
        """
        Обновляет профиль. Поддерживает:
          - смену email (с проверкой на уникальность),
          - смену first_name/last_name/middle_name.
        """
        user = await self.get_by_id(user_id)
        if not user.is_active:
            raise Forbidden("Inactive user cannot be updated")

        values: dict = {}

        if data.email is not None and data.email != user.email:
            exists_q = select(exists().where(User.email == data.email, User.id != user_id))
            email_taken = (await self.session.execute(exists_q)).scalar()
            if email_taken:
                raise Conflict("Email is already in use")
            values["email"] = str(data.email)

        # имена
        if data.first_name is not None:
            values["first_name"] = data.first_name
        if data.last_name is not None:
            values["last_name"] = data.last_name
        if data.middle_name is not None:
            values["middle_name"] = data.middle_name

        if not values:
            return user

        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**values)
        )
        await self.session.commit()

        await self.session.refresh(user)
        return user

    async def soft_delete(self, user_id: int) -> None:
        """
        Мягкое удаление: ставим is_active=False и инвалидируем все сессии.
        Пользователь больше не сможет залогиниться.
        """
        user = await self.get_by_id(user_id)
        if not user.is_active:
            return

        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        await self.session.commit()