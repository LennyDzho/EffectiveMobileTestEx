from dishka import make_async_container
from dishka.integrations.fastapi import DishkaRoute, FastapiProvider, setup_dishka
from fastapi import APIRouter, Depends, FastAPI

from .auth import AuthProvider
from ..guards import require_user

from ..providers.db_provider import DatabaseProvider



api_router = APIRouter(
    prefix="/api",
    route_class=DishkaRoute,
    dependencies=[Depends(require_user)]
)


def setup_container(app: FastAPI) -> None:
    container = make_async_container(
        FastapiProvider(),
        DatabaseProvider(),
        AuthProvider(),
    )

    setup_dishka(container, app)


__all__ = ["api_router", "setup_container"]
