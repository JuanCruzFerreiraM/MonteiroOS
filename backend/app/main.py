from fastapi import FastAPI

from app.api.health import router as health_router
from app.core.access import DeploymentAccessMiddleware
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name)
    application.add_middleware(
        DeploymentAccessMiddleware,
        secret=settings.app_access_secret.strip(),
    )
    application.include_router(health_router)
    return application


app = create_app()
