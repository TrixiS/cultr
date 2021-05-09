import secrets

from typing import List, Optional
from pydantic import BaseSettings, AnyHttpUrl, EmailStr


class Settings(BaseSettings):

    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 1
    CORS_ORIGINS: List[AnyHttpUrl] = ["http://localhost:3000"]
    DATABASE_URI: str = "sqlite+aiosqlite:///database.db"

    EMAILS_ON: bool = False
    EMAIL_USER: Optional[EmailStr]
    EMAIL_PASS: Optional[str]
    EMAIL_HOST: Optional[str]
    EMAIL_PORT: Optional[int]

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
