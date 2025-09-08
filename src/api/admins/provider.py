from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession

from .services import AdminService

class AdminsProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def service(self, session: AsyncSession) -> AdminService:
        return AdminService(session)