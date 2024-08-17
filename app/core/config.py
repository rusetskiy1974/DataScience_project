from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    DATABASE_URL: Optional[str]
    HOST: Optional[str] = "127.0.0.1"
    PORT: Optional[int] = 8000
    POSTGRES_USER: Optional[str]
    POSTGRES_PASSWORD: Optional[str]
    POSTGRES_DB: Optional[str]
    POSTGRES_HOST: Optional[str]
    POSTGRES_PORT: Optional[int]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

if (
    settings.DATABASE_URL is None
    or settings.POSTGRES_USER is None
    or settings.POSTGRES_PASSWORD is None
    or settings.POSTGRES_DB is None
    or settings.POSTGRES_HOST is None
    or settings.POSTGRES_PORT is None
):
    raise ValueError("Some required settings are missing")
