from pydantic import BaseModel

from .base import DBBaseModel


class User(DBBaseModel):
    id: int
    username: str
    hashed_password: str


class UserIn(BaseModel):
    username: str
    password: str
