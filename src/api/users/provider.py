from dishka import Provider, provide, Scope

from sqlalchemy.ext.asyncio import AsyncSession
from src.api.auth.services import AuthService
from src.api.users.services import UserService


class UsersProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def user_service(self, session: AsyncSession, auth_service: AuthService) -> UserService:
        return UserService(session=session, auth_service=auth_service)
