from functools import lru_cache
from pathlib import Path
from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_ROOT.parent

_ENV_FILES = tuple(
    path for path in (REPO_ROOT / ".env", BACKEND_ROOT / ".env") if path.is_file()
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILES or None,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Monteiro OS"
    app_env: str = "development"
    database_url: str | None = None
    postgres_user: str = "monteiro"
    postgres_password: str = "monteiro"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "monteiro"

    @property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url
        user = quote_plus(self.postgres_user)
        password = quote_plus(self.postgres_password)
        return (
            f"postgresql+psycopg://{user}:{password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
