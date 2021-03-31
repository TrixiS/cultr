import uuid

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.security.base import SecurityBase

from pydantic import BaseModel
from passlib.context import CryptContext

from ..database import database
from ..database.models import users, sessions

PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    username: str
    password: str


class Session(BaseModel):
    username: str
    token: str

    @classmethod
    def from_username(cls, username):
        return cls(username=username, token=uuid.uuid1().hex)


class CookieAuth(SecurityBase):

    def __init__(self):
        self.scheme_name = self.__class__.__name__

    async def __call__(self, request: Request) -> Session:
        token = request.cookies.get("Authorization")
        error_403 = HTTPException(status_code=403)

        if token is None:
            raise error_403

        select_query = sessions.select().where(sessions.c.token == token)
        session = await database.fetch_one(select_query)

        if session is None:
            raise error_403

        return session


cookie_auth = CookieAuth()
router = APIRouter()


def set_auth_cookie(response: Response, session: Session):
    response.set_cookie("Authorization", session.token)


async def insert_session(session):
    query = sessions.insert().values(username=session.username, token=session.token)
    await database.execute(query)


async def fetch_user(username):
    query = users.select().where(users.c.username == username)
    return await database.fetch_one(query)


@router.post("/register", response_model=Session, status_code=201)
async def register(user: User, response: Response):
    db_user = await fetch_user(user.username)

    if db_user is not None:
        raise HTTPException(409, "User already exists")

    session = Session.from_username(user.username)

    insert_user_query = users.insert().values(
        username=user.username,
        hashed_password=PASSWORD_CONTEXT.hash(user.password)
    )

    set_auth_cookie(response, session)
    await database.execute(insert_user_query)
    await insert_session(session)

    return session


@router.post("/login", response_model=Session, status_code=201)
async def login(user: User, response: Response):
    db_user = await fetch_user(user.username)

    if db_user is None:
        raise HTTPException(401)

    session = Session.from_username(user.username)
    set_auth_cookie(response, session)
    await insert_session(session)

    return session
