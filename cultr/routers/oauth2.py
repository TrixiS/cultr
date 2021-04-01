import os
import datetime as dt

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.encoders import jsonable_encoder

from pydantic import BaseModel
from passlib.context import CryptContext
from jose import jwt

from ..database import database
from ..database.models import users

PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")


class User(BaseModel):
    id: int
    username: str
    hashed_password: str


class UserIn(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


async def fetch_user(username):
    user_select_query = users.select().where(users.c.username == username)
    return await database.fetch_one(user_select_query)


async def current_user(token: str = Depends(oauth2_scheme)) -> User:
    error_401 = HTTPException(401, headers={"WWW-Authenticate": "Bearer"})

    try:
        decoded_user_dict = jwt.decode(
            token,
            os.environ["JWT_SECRET"],
            algorithms=[os.environ["JWT_ALGO"]]
        )
    except jwt.JWTError:
        raise error_401

    expires_datetime = dt.datetime.fromisoformat(decoded_user_dict["expires_at"])

    if expires_datetime <= dt.datetime.utcnow():
        raise error_401

    db_user = await fetch_user(decoded_user_dict["username"])

    if db_user is None:
        raise error_401

    return db_user


def create_access_token(user_data, expires_timedelta=None):
    to_encode = user_data.copy()

    if expires_timedelta is not None:
        expires_at = dt.datetime.utcnow() + expires_timedelta
    else:
        expires_at = dt.datetime.utcnow() + dt.timedelta(minutes=int(os.environ["TOKEN_EXPIRE_MINUTES"]))

    to_encode["expires_at"] = expires_at

    return jwt.encode(
        jsonable_encoder(to_encode),
        os.environ["JWT_SECRET"],
        algorithm=os.environ["JWT_ALGO"]
    )


@router.post("/token", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await fetch_user(form_data.username)
    error_400 = HTTPException(400, "Incorrect username or password")

    if db_user is None:
        raise error_400

    if not PASSWORD_CONTEXT.verify(form_data.password, db_user.hashed_password):
        raise error_400

    token = create_access_token({"username": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/users", status_code=201)
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await fetch_user(form_data.username)

    if db_user is not None:
        raise HTTPException(409, "User already exists")

    insert_user_query = users.insert().values(
        username=form_data.username,
        hashed_password=PASSWORD_CONTEXT.hash(form_data.password)
    )

    await database.execute(insert_user_query)
    return {"detail": "Success"}


@router.get("/secret")
async def get_secret(user: User = Depends(current_user)):
    return {"secret": os.environ["JWT_SECRET"]}
