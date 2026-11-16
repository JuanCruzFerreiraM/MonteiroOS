from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.health import router as health_router
from app.core.access import DeploymentAccessMiddleware
from app.core.config import get_settings
from app.modules.production.routes import router as production_router
from app.modules.production.rules import DomainError


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name)
    application.add_middleware(
        DeploymentAccessMiddleware,
        secret=settings.app_access_secret.strip(),
    )
    application.add_exception_handler(DomainError, domain_error_response)
    application.include_router(health_router)
    application.include_router(production_router)
    return application


def domain_error_response(_request: Request, exc: DomainError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


app = create_app()
