from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    SECRET_KEY: str
    ALGORITHM: str
    PARKING_HOURLY_RATE: int = 20
    CREDIT_LIMIT: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
