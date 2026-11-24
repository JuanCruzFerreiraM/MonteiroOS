from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import ProgrammingError

from app.api.health import router as health_router
from app.core.access import DeploymentAccessMiddleware
from app.core.config import get_settings
from app.modules.production.routes import router as production_router
from app.modules.production.rules import DomainError

SCHEMA_NOT_APPLIED_DETAIL = (
    "El esquema de producción no está aplicado. Ejecute alembic upgrade head."
)
DATABASE_QUERY_FAILED_DETAIL = "No se pudo consultar la base de datos."


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name)
    application.add_middleware(
        DeploymentAccessMiddleware,
        secret=settings.app_access_secret.strip(),
    )
    application.add_exception_handler(DomainError, domain_error_response)
    application.add_exception_handler(ProgrammingError, database_programming_error)
    application.include_router(health_router)
    application.include_router(production_router)
    return application


def domain_error_response(_request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


def database_programming_error(
    _request: Request,
    exc: ProgrammingError,
) -> JSONResponse:
    """Hide SQL when the production tables have not been created yet."""
    if _missing_relation(exc):
        return JSONResponse(
            status_code=503,
            content={"detail": SCHEMA_NOT_APPLIED_DETAIL},
        )
    return JSONResponse(
        status_code=500,
        content={"detail": DATABASE_QUERY_FAILED_DETAIL},
    )


def _missing_relation(exc: ProgrammingError) -> bool:
    orig = exc.orig
    sqlstate = getattr(orig, "sqlstate", None)
    if sqlstate in {"42P01", "42703"}:
        return True
    return type(orig).__name__ in {"UndefinedTable", "UndefinedColumn"}


app = create_app()
