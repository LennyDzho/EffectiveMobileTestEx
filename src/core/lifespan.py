import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI


from .taskiq_broker import broker
from ..database import db_helper
from ..startup.add_admin import create_default_admins

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    # Startup

    logger.info("Starting application....")
    await create_default_admins()
    if not broker.is_worker_process:
        await broker.startup()
    yield
    if not broker.is_worker_process:
        await broker.shutdown()
    await db_helper.dispose()
    await app.state.dishka_container.close()

    logger.info("Application shutdown complete.")
