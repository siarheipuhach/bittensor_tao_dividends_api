from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application environment settings, loaded from .env file or environment variables."""

    redis_url: str = "redis://localhost:6379"
    chutes_api_key: str = "dummy"
    datura_api_key: str = "dummy"
    auth_token: str = "test"
    postgres_dsn: str = "postgresql+asyncpg://postgres:postgres@db:5432/postgres"

    class Config:
        env_file = ".env"


settings = Settings()
