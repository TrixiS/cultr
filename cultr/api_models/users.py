from typing import Optional
from pydantic import BaseModel, EmailStr, validator, Field


class Username(BaseModel):
    username: str = Field(min_length=1, max_length=25)


class UserBase(Username):
    email: EmailStr


class User(UserBase):
    id: int
    hashed_password: str
    email_confirmed: bool

    class Config:
        orm_mode = True


class UserIn(UserBase):
    password: str


class UserUpdate(Username):
    password: Optional[str] = Field(None, min_length=1)
    new_password: Optional[str] = Field(None, min_length=1)

    @validator("new_password")
    def original_password_set(cls, v, values):
        if v is not None:
            assert values.get(
                "password") is not None, "To update password, original password should be set"

        return v
