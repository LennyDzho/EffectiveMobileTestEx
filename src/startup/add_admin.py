import logging

import bcrypt
from sqlalchemy import select
from src.database import db_helper
from src.database.models import User
from src.database.models.admins import Admin

logger = logging.getLogger("Startup task")


async def create_default_admins() -> None:
    """
    Создаёт двух пользователей:
    - superadmin@example.com (суперадмин)
    - admin@example.com (обычный админ)
    Если пользователи уже есть — только обновит статусы.
    """
    async with db_helper.session_factory() as session:
        # ---- SUPER ADMIN ----
        super_email = "superadmin@example.com"
        super_pass = "superpass"

        super_user = await session.scalar(select(User).where(User.email == super_email))
        if not super_user:
            salt = bcrypt.gensalt(rounds=12)
            super_user = User(
                email=super_email,
                password_hash=bcrypt.hashpw(super_pass.encode("utf-8"), salt).decode("utf-8"),
                first_name="Super",
                last_name="Admin",
                is_active=True,
            )
            session.add(super_user)
            await session.flush()
            logger.info("Создан супер-админ: %s", super_email)

        super_admin = await session.scalar(select(Admin).where(Admin.user_id == super_user.id))
        if not super_admin:
            super_admin = Admin(user_id=super_user.id, super_admin=True)
            session.add(super_admin)
        else:
            super_admin.super_admin = True

        # ---- ORDINARY ADMIN ----
        admin_email = "admin@example.com"
        admin_pass = "adminpass"

        admin_user = await session.scalar(select(User).where(User.email == admin_email))
        if not admin_user:
            salt = bcrypt.gensalt(rounds=12)
            admin_user = User(
                email=admin_email,
                password_hash=bcrypt.hashpw(admin_pass.encode("utf-8"), salt).decode("utf-8"),
                first_name="Normal",
                last_name="Admin",
                is_active=True,
            )
            session.add(admin_user)
            await session.flush()
            logger.info("Создан админ: %s", admin_email)

        admin = await session.scalar(select(Admin).where(Admin.user_id == admin_user.id))
        if not admin:
            admin = Admin(user_id=admin_user.id, super_admin=False)
            session.add(admin)
        else:
            admin.super_admin = False

        await session.commit()
        logger.info("Созданы/обновлены супер-админ и админ.")
