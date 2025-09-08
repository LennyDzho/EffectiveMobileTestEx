from typing import Optional, Sequence

from sqlalchemy import select, update, delete, exists
from sqlalchemy.exc import IntegrityError

from src.database.models.admins import Admin
from src.database.repositories import BaseRepo


class AdminRepository(BaseRepo):
    """Репозиторий для работы с администраторами."""

    # --------- GETTERS ---------
    async def get_by_id(self, admin_id: int) -> Optional[Admin]:
        stmt = select(Admin).where(Admin.id == admin_id)
        return await self.session.scalar(stmt)

    async def get_by_user_id(self, user_id: int) -> Optional[Admin]:
        stmt = select(Admin).where(Admin.user_id == user_id)
        return await self.session.scalar(stmt)

    async def list_admins(self) -> Sequence[Admin]:
        result = await self.session.execute(select(Admin))
        return result.scalars().all()

    async def is_admin(self, user_id: int) -> bool:
        stmt = select(exists().where(Admin.user_id == user_id))
        return bool((await self.session.execute(stmt)).scalar())

    async def is_super_admin(self, user_id: int) -> bool:
        stmt = select(exists().where(Admin.user_id == user_id, Admin.super_admin.is_(True)))
        return bool((await self.session.execute(stmt)).scalar())

    # --------- MUTATORS ---------
    async def add_admin(self, user_id: int, *, super_admin: bool = False) -> Admin:
        """
        Создаёт администратора для user_id.
        Бросает IntegrityError, если user_id уже админ (уникальный индекс на user_id).
        """
        admin = Admin(user_id=user_id, super_admin=super_admin)
        self.add(admin)
        try:
            await self.commit()
        except IntegrityError:
            await self.rollback()
            existing = await self.get_by_user_id(user_id)
            if existing:
                return existing
            raise
        await self.session.refresh(admin)
        return admin

    async def remove_admin(self, user_id: int) -> None:
        """Удаляет запись администратора по user_id (молчаливо, если её нет)."""
        await self.session.execute(delete(Admin).where(Admin.user_id == user_id))
        await self.commit()

    async def set_super_admin(self, user_id: int, value: bool = True) -> Optional[Admin]:
        """
        Проставляет/снимает флаг super_admin.
        Возвращает обновлённую запись или None, если админ не найден.
        """
        await self.session.execute(
            update(Admin)
            .where(Admin.user_id == user_id)
            .values(super_admin=value)
        )
        await self.commit()
        return await self.get_by_user_id(user_id)