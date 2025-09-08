from fastapi import Depends, Request

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.services import AuthService, COOKIE_NAME
from src.core.infra.exceptions import NotAuthenticated, Forbidden

from src.database import db_helper
from src.database.models import User
from src.database.repositories.admins import AdminRepository

def get_admin_repo(
    db: AsyncSession = Depends(db_helper.get_session),
) -> AdminRepository:
    return AdminRepository(db)

async def require_user(
    request: Request,
    db: AsyncSession = Depends(db_helper.get_session),
) -> User:
    sid = request.cookies.get(COOKIE_NAME)
    if not sid:
        raise NotAuthenticated()
    service = AuthService(db)
    return await service.get_current_user(sid)


async def require_admin(
    current_user: User = Depends(require_user),
    repo: AdminRepository = Depends(get_admin_repo),
) -> User:
    if not await repo.is_admin(current_user.id):
        raise Forbidden("Administrator rights required")
    return current_user


async def require_super_admin(
    current_user: User = Depends(require_user),
    repo: AdminRepository = Depends(get_admin_repo),
) -> User:
    if not await repo.is_super_admin(current_user.id):
        raise Forbidden("Super admin rights required")
    return current_user