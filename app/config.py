from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    chutes_api_key: str = "dummy"
    datura_api_key: str = "dummy"
    auth_token: str = "test"

    class Config:
        env_file = ".env"


settings = Settings()
