import logging
from fastapi import Request, status, Response

from src.core.infra import ErrorJsonResponse, ErrorStatus

logger = logging.getLogger(__name__)


async def not_authenticated_exception_handler(_request: Request, _exc: Exception) -> Response:

    return ErrorJsonResponse(
        code=status.HTTP_401_UNAUTHORIZED,
        message="Not Authenticated",
        status=ErrorStatus.UNAUTHENTICATED,
    )

async def invalid_authenticated_exception_handler(
    _request: Request, _exc: Exception
) -> Response:
    return ErrorJsonResponse(
        code=status.HTTP_403_FORBIDDEN,
        message="Invalid authenticated credentials",
        status=ErrorStatus.PERMISSION_DENIED,
    )

async def http_exception_handler(_request: Request, exc: Exception):

    logger.error(
        "HTTPException: %s %s",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        exc,
    )

    return ErrorJsonResponse(
        code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Internal server error",
        status=ErrorStatus.INTERNAL,
    )