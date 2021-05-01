import datetime as dt

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from passlib.context import CryptContext
from jose import jwt

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import api_models
from ..config import settings
from ..database import get_session, models as db_models

PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGO = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


def create_jwt_from_data(data):
    return jwt.encode(data, settings.SECRET_KEY, algorithm=ALGO)


def decode_jwt(token):
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGO]
        )
    except jwt.JWTError:
        return None


def create_access_token(user_data, expires_timedelta=None):
    to_encode = user_data.copy()

    if expires_timedelta is not None:
        expires_at = dt.datetime.utcnow() + expires_timedelta
    else:
        expires_at = dt.datetime.utcnow(
        ) + dt.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode["exp"] = expires_at.timestamp()
    return create_jwt_from_data(to_encode)


async def current_user(
    *,
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme)
) -> api_models.User:
    error_401 = HTTPException(401, headers={"WWW-Authenticate": "Bearer"})
    decoded_user_dict = decode_jwt(token)

    if decoded_user_dict is None or "exp" not in decoded_user_dict:
        raise error_401

    expires_datetime = dt.datetime.utcfromtimestamp(decoded_user_dict["exp"])

    if expires_datetime <= dt.datetime.utcnow():
        raise error_401

    select_query = select(
        db_models.User).filter_by(
        username=decoded_user_dict["sub"])
    result = await session.execute(select_query)
    db_user = result.scalar()

    if db_user is None:
        raise error_401

    if not db_user.email_confirmed:
        raise HTTPException(403, "Email is not confirmed")

    return api_models.User.from_orm(db_user)
