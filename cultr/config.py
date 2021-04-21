import secrets

from typing import List
from pydantic import BaseSettings, AnyHttpUrl


class Settings(BaseSettings):

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1
    CORS_ORIGINS: List[AnyHttpUrl] = []
    DATABASE_URI: str

    class Config:
        case_sensitive = True


settings = Settings()
