from dishka import Provider, provide, Scope
from sqlalchemy.ext.asyncio import AsyncSession

from .services import AuthService


class AuthProvider(Provider):
    """DI-провайдер для AuthService."""
    scope = Scope.REQUEST

    @provide
    async def service_provider(self, session: AsyncSession) -> AuthService:
        return AuthService(session)