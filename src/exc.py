from fastapi import HTTPException, Request, FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, Dict


class ServiceUnavailableError(HTTPException):
    pass


class DataNotFoundException(HTTPException):
    pass


async def exc_handler(
    request: Request,
    exc: HTTPException,
    content: Dict[str, Any],
    status_code: int = None,
):
    code = (
        status_code
        if status_code is not None
        else getattr(exc, "status_code", status.HTTP_500_INTERNAL_SERVER_ERROR)
    )
    return JSONResponse(status_code=code, content=content)


async def requestvalidation(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    content = {"error": "Validation failed", "details": errors}
    return await exc_handler(
        request, exc, content=content, status_code=status.HTTP_400_BAD_REQUEST
    )


async def service_unavailable(request: Request, exc: ServiceUnavailableError):
    content = {"error": "External data source unavailable", "details": exc.detail}
    return await exc_handler(
        request, exc, content=content, status_code=status.HTTP_503_SERVICE_UNAVAILABLE
    )


async def not_found(request: Request, exc: DataNotFoundException):
    content = {"error": "Country not found", "details": exc.detail}
    return await exc_handler(
        request, exc, content=content, status_code=status.HTTP_404_NOT_FOUND
    )


async def starlette_validation(request: Request, exc: StarletteHTTPException):
    detail_str = str(exc.detail).lower() if exc.detail else ""
    if exc.status_code == 404:
        return await exc_handler(
            request,
            exc,
            {"error": "Country not found", "details": str(exc)},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if any(
        phrase in detail_str
        for phrase in ["malformed", "json", "body", "parse error", "invalid json"]
    ):
        return await exc_handler(
            request,
            exc,
            {"error": "Malformed or invalid JSON body"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    return JSONResponse(
        {"error": "HTTP error", "details": str(exc)}, status_code=exc.status_code
    )


def register_exc(app: FastAPI):
    app.add_exception_handler(DataNotFoundException, not_found)
    app.add_exception_handler(ServiceUnavailableError, service_unavailable)
    app.add_exception_handler(RequestValidationError, requestvalidation)
    app.add_exception_handler(StarletteHTTPException, starlette_validation)
