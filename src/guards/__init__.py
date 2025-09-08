from fastapi import Depends, Request

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.services import AuthService, COOKIE_NAME
from src.core.infra.exceptions import NotAuthenticated
from src.database import db_helper
from src.database.models import User

async def require_user(
    request: Request,
    db: AsyncSession = Depends(db_helper.get_session),
) -> User:
    sid = request.cookies.get(COOKIE_NAME)
    if not sid:
        raise NotAuthenticated()
    service = AuthService(db)
    return await service.get_current_user(sid)