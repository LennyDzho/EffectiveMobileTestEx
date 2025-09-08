from dishka import make_async_container
from dishka.integrations.fastapi import DishkaRoute, FastapiProvider, setup_dishka
from fastapi import APIRouter, Depends, FastAPI

from .auth import AuthProvider
from .users import UsersProvider
from ..guards import require_user

from ..providers.db_provider import DatabaseProvider

from .users import users_router


api_router = APIRouter(
    prefix="/api",
    route_class=DishkaRoute,
    dependencies=[Depends(require_user)]
)

api_router.include_router(users_router)


def setup_container(app: FastAPI) -> None:
    container = make_async_container(
        FastapiProvider(),
        DatabaseProvider(),
        AuthProvider(),
        UsersProvider(),
    )

    setup_dishka(container, app)


__all__ = ["api_router", "setup_container"]
