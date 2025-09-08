from fastapi import Depends, Request
from typing import Annotated

from src.api.auth.services import AuthService, COOKIE_NAME
from src.core.infra.exceptions import NotAuthenticated
from src.database.models import User

async def require_user(
    request: Request,
    service: Annotated[AuthService, Depends()],
) -> User:
    sid = request.cookies.get(COOKIE_NAME)
    if not sid:
        raise NotAuthenticated()
    return await service.get_current_user(sid)