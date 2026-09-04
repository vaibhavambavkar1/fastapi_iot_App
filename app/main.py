import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.core.logging import setup_logging
from app.db.session import Base, engine

# Import models so SQLAlchemy can register them.
import app.models  # noqa: F401

settings = get_settings()
logger = logging.getLogger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()

    # For real projects, prefer Alembic migrations.
    if settings.environment.lower() in {"local", "dev"}:
        Base.metadata.create_all(bind=engine)

    yield


app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = request_id

    start_time = time.perf_counter()

    response = await call_next(request)

    duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

    response.headers["X-Request-ID"] = request_id

    logger.info(
        "Request completed",
        extra={
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
        },
    )

    return response


def error_response(
    status_code: int,
    code: str,
    message: str,
    details=None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details,
            }
        },
    )


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return error_response(
        status_code=exc.status_code,
        code=exc.error_code,
        message=exc.message,
        details=exc.details,
    )


@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
):
    return error_response(
        status_code=422,
        code="validation_error",
        message="Request validation failed.",
        details=exc.errors(),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
):
    return error_response(
        status_code=exc.status_code,
        code="http_error",
        message=str(exc.detail),
    )


app.include_router(
    api_router,
    prefix=settings.api_v1_prefix,
)
