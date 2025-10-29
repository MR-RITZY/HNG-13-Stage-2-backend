from fastapi import HTTPException, Request, FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ServiceUnavailableError(HTTPException):
    pass

class DataNotFoundException(HTTPException):
    pass


async def exc_handler(request: Request, exc:HTTPException, content:dict):
    return JSONResponse(
        status_code=exc.status_code, content=content
    )

async def requestvalidation(request: Request, exc:RequestValidationError):
    content = {
        "error":"Validation failed", "details": exc.errors
    }
    return await exc_handler(request, exc, content=content)

async def service_unavailable(request: Request, exc:ServiceUnavailableError):
    content = {
        "error":"External data source unavailable", "details": exc.detail
    }
    return await exc_handler(request, exc, content=content)

async def not_found(request: Request, exc:DataNotFoundException):
    content = {
        "error":"Country not found", "details": exc.detail
    }
    return await exc_handler(request, exc, content=content)


def register_exc(app:FastAPI):
    app.add_exception_handler(DataNotFoundException, not_found)
    app.add_exception_handler(ServiceUnavailableError, service_unavailable)
    app.add_exception_handler(RequestValidationError, requestvalidation)
