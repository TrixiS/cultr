import datetime as dt

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordBearer

from passlib.context import CryptContext
from jose import jwt

from .. import api_models
from ..config import settings
from .db import fetch_user

PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGO = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


def create_access_token(user_data, expires_timedelta=None):
    to_encode = user_data.copy()

    if expires_timedelta is not None:
        expires_at = dt.datetime.utcnow() + expires_timedelta
    else:
        expires_at = dt.datetime.utcnow(
        ) + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode["exp"] = expires_at.timestamp()

    return jwt.encode(
        jsonable_encoder(to_encode),
        settings.SECRET_KEY,
        algorithm=ALGO
    )


async def current_user(token: str = Depends(oauth2_scheme)) -> api_models.User:
    error_401 = HTTPException(401, headers={"WWW-Authenticate": "Bearer"})

    try:
        decoded_user_dict = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGO]
        )
    except jwt.JWTError:
        raise error_401

    expires_datetime = dt.datetime.fromtimestamp(decoded_user_dict["exp"])

    if expires_datetime <= dt.datetime.utcnow():
        raise error_401

    db_user = await fetch_user(decoded_user_dict["sub"])

    if db_user is None:
        raise error_401

    return api_models.User.from_orm(db_user)
