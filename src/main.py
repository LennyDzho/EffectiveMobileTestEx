import logging

import uvicorn

from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference
from starlette.responses import RedirectResponse

from src.api import setup_container, api_router
from src.api.auth import auth_router

from src.api.exception_handlers import not_authenticated_exception_handler, invalid_authenticated_exception_handler, \
    http_exception_handler
from src.core import setup_logging, settings, lifespan

from src.core.infra.exceptions import NotAuthenticated, InvalidCredentials

logger = logging.getLogger(__name__)

setup_logging(settings.app.debug)


app = FastAPI(
    debug=settings.app.debug,
    lifespan=lifespan,
    title="EffectiveMobile Auth API",
    version="0.1.0beta",
    docs_url="/swagger",
    redoc_url=None,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)


setup_container(app)

# 401
app.add_exception_handler(NotAuthenticated, not_authenticated_exception_handler)

# 403
app.add_exception_handler(InvalidCredentials, invalid_authenticated_exception_handler)

# 500
app.add_exception_handler(Exception, http_exception_handler)

@app.get("/", include_in_schema=False)
async def redirect_to_docs() -> RedirectResponse:
    return RedirectResponse("/docs")

@app.get("/docs", include_in_schema=False)
async def init_scalar_docs():
    return get_scalar_api_reference(
        title=app.title,  # type: ignore
        openapi_url=app.openapi_url,  # type: ignore
        hide_models=True,
        hide_download_button=True,
    )

app.include_router(auth_router)
app.include_router(api_router)


if __name__ == "__main__":
    try:
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except (KeyboardInterrupt, SystemExit):
        pass