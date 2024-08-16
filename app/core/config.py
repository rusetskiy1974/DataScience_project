from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    HOST: str
    PORT: int = 8000
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
