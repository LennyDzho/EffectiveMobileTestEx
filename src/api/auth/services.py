import logging
import datetime

import secrets
from typing import Optional

import bcrypt
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.infra.exceptions import (
    Conflict,
    InvalidCredentials,
    NotAuthenticated,
    SessionExpired,
    NotFound,
    InactiveUser,
)
from src.database.models import User
from src.redis_storage.repositories import RedisRepo


logger = logging.getLogger(__name__)


COOKIE_NAME = "sessionid"
DEFAULT_SESSION_TTL = 12 * 3600  # время активности сессии


class AuthService:
    """
    Сервис аутентификации/сессий.
    - хранит пользователей в БД,
    - серверные сессии в Redis: sess:{sid} -> { user_id, issued_at, expires_at, ... }
    """

    def __init__(self, session: AsyncSession, *, session_ttl: int = DEFAULT_SESSION_TTL) -> None:
        self.session = session
        self.session_ttl = session_ttl

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def _check_password(password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
        except Exception as e:
            logger.exception("Error checking password: %s", e)
            return False

    async def _create_session(self, user_id: int) -> str:
        """Создаёт серверную сессию в Redis и возвращает SID (значение для cookie)."""
        sid = secrets.token_urlsafe(32)
        repo = RedisRepo(prefix="sess", key=sid, ttl=self.session_ttl)

        now = datetime.datetime.now(datetime.UTC)

        payload = {
            "user_id": str(user_id),
            "issued_at": now.isoformat(),
            "expires_at": (now + datetime.timedelta(seconds=self.session_ttl)).isoformat(),
        }
        await repo.h_set(payload)
        return sid
    async def _delete_session(self, sid: str) -> None:
        repo = RedisRepo(prefix="sess", key=sid, ttl=self.session_ttl)
        await repo.delete()

    async def register(
            self,
            email: str,
            password: str,
            *,
            first_name: str,
            last_name: str,
            middle_name: Optional[str] = None,
    ) -> User:
        """Создаёт нового пользователя. Бросает Conflict, если email занят."""
        email_norm = email.strip().lower()

        exists_stmt = select(func.count()).select_from(User).where(User.email == email_norm)
        (count,) = (await self.session.execute(exists_stmt)).one()
        if count:
            raise Conflict("User with this email already exists")

        user = User(
            email=email_norm,
            password_hash=self._hash_password(password),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            middle_name=(middle_name.strip() if middle_name else None),
            is_active=True,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def login(self, email: str, password: str) -> str:
        """
        Проверяет логин/пароль, возвращает SID (значение для Set-Cookie).
        Исключения:
          - InvalidCredentials — если пары (email, password) нет
          - InactiveUser — если пользователь заблокирован
        """
        stmt = select(User).where(User.email == email)
        user = await self.session.scalar(stmt)
        if not user or not self._check_password(password, user.password_hash):
            raise InvalidCredentials()

        if not user.is_active:
            raise InactiveUser()

        sid = await self._create_session(user.id)
        return sid

    async def logout_by_sid(self, sid: Optional[str]) -> None:
        """Логаут по SID из cookie. Если SID нет — NotAuthenticated."""
        if not sid:
            raise NotAuthenticated()
        await self._delete_session(sid)

    async def get_current_user(self, sid: Optional[str]) -> User:
        """
        Возвращает пользователя по SID. Бросает:
          - NotAuthenticated — если SID отсутствует
          - SessionExpired — если сессия не найдена/протухла/битая
          - NotFound — если пользователь удалён
          - InactiveUser — если пользователь заблокирован
        """
        if not sid:
            raise NotAuthenticated()

        repo = RedisRepo(prefix="sess", key=sid, ttl=self.session_ttl)
        raw = await repo.h_get_all()
        if not raw:
            # либо TTL истёк, либо ключ удалён
            raise SessionExpired()

        data = {k.decode(): v.decode() for k, v in raw.items()}
        user_id = data.get("user_id")
        if not user_id:
            raise SessionExpired(detail="Missing user_id in session")

        user = await self.session.scalar(select(User).where(User.id == int(user_id)))
        if not user:
            raise NotFound("User not found")
        if not user.is_active:
            raise InactiveUser()

        # продлеваем сессию
        await repo.redis.expire(repo._key(), self.session_ttl)

        return user