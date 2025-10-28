from functools import lru_cache
from typing import List, Optional

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "Secret Santa API"
    database_url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field("redis://redis:6379/0", env="REDIS_URL")
    smtp_host: str = Field(..., env="SMTP_HOST")
    smtp_port: int = Field(465, env="SMTP_PORT")
    smtp_username: str = Field(..., env="SMTP_USERNAME")
    smtp_password: str = Field(..., env="SMTP_PASSWORD")
    smtp_sender: str = Field("Secret Santa <no-reply@santa.local>", env="SMTP_SENDER")
    jwt_secret: str = Field(..., env="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    public_base_url: str = Field("https://santa.example.com", env="PUBLIC_BASE_URL")
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])
    celery_broker_url: str = Field("redis://redis:6379/0", env="CELERY_BROKER_URL")
    celery_result_backend: str = Field("redis://redis:6379/0", env="CELERY_RESULT_BACKEND")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
