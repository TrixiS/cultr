from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel

router = APIRouter()


class UserIn(BaseModel):
    username: str
    password: str


@router.post("/register")
async def register(user: UserIn):
    return {"Hello": "World"}


@router.get("/register")
async def register():
    return {"Hello": "World"}
