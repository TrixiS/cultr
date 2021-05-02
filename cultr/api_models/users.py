from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str


class User(UserBase):
    id: int
    hashed_password: str
    email_confirmed: bool

    class Config:
        orm_mode = True


class UserIn(UserBase):
    password: str
