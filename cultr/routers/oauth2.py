import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder

from passlib.context import CryptContext
from jose import jwt

from .. import config
from ..models.token import Token
from ..models.users import User, UserIn
from ..database import models as db_models, async_session
from ..utils.db import fetch_user

PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


async def current_user(token: str = Depends(oauth2_scheme)) -> User:
    error_401 = HTTPException(401, headers={"WWW-Authenticate": "Bearer"})

    try:
        decoded_user_dict = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=[config.JWT_ALGO]
        )
    except jwt.JWTError:
        raise error_401

    expires_datetime = dt.datetime.fromisoformat(
        decoded_user_dict["expires_at"])

    if expires_datetime <= dt.datetime.utcnow():
        raise error_401

    db_user = await fetch_user(decoded_user_dict["sub"])

    if db_user is None:
        raise error_401

    return User.from_db_model(db_user)


def create_access_token(user_data, expires_timedelta=None):
    to_encode = user_data.copy()

    if expires_timedelta is not None:
        expires_at = dt.datetime.utcnow() + expires_timedelta
    else:
        expires_at = dt.datetime.utcnow(
        ) + dt.timedelta(minutes=config.JWT_EXPIRE_MINUTES)

    to_encode["expires_at"] = expires_at

    return jwt.encode(
        jsonable_encoder(to_encode),
        config.JWT_SECRET,
        algorithm=config.JWT_ALGO
    )


@router.post("/token", response_model=Token, status_code=201)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await fetch_user(form_data.username)
    error_400 = HTTPException(400, "Incorrect username or password")

    if db_user is None:
        raise error_400

    if not PASSWORD_CONTEXT.verify(
            form_data.password, db_user.hashed_password):
        raise error_400

    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/users", status_code=201)
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    async with async_session() as session:
        db_user = await fetch_user(form_data.username, session)

        if db_user is not None:
            raise HTTPException(409, "User already exists")

        user = db_models.User(
            username=form_data.username,
            hashed_password=PASSWORD_CONTEXT.hash(form_data.password)
        )

        session.add(user)
        await session.commit()

    return Response(status_code=201)
