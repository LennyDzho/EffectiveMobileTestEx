from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.infra.exceptions import NotFound, Conflict
from src.database.models import User
from src.database.repositories.admins import AdminRepository
from src.api.admins.schemas import AdminCreateIn
from src.database.models.admins import Admin


class AdminService:
    """
    Бизнес-логика управления администраторами.
    Работает через AdminRepository. При добавлении админа проверяет,
    что пользователь существует.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = AdminRepository(session)

    # ---------- queries ----------
    async def list_admins(self) -> list[Admin]:
        return list(await self.repo.list_admins())

    async def get_by_user_id(self, user_id: int) -> Admin:
        admin = await self.repo.get_by_user_id(user_id)
        if not admin:
            raise NotFound("Admin not found")
        return admin

    # ---------- commands ----------
    async def add_admin(self, data: AdminCreateIn) -> Admin:
        user = await self.session.scalar(select(User).where(User.id == data.user_id))
        if not user:
            raise NotFound("User not found")

        existing = await self.repo.get_by_user_id(data.user_id)
        if existing:
            raise Conflict("User is already an admin")

        admin = await self.repo.add_admin(user_id=data.user_id, super_admin=data.super_admin)
        return admin

    async def remove_admin(self, user_id: int) -> None:
        await self.repo.remove_admin(user_id)

    async def set_super_admin(self, user_id: int, value: bool) -> Admin:
        admin = await self.repo.get_by_user_id(user_id)
        if not admin:
            raise NotFound("Admin not found")
        updated = await self.repo.set_super_admin(user_id, value)
        if not updated:
            raise NotFound("Admin not found after update")
        return updated