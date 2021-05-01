from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str


class User(UserBase):
    id: int
    hashed_password: str

    class Config:
        orm_mode = True


class UserIn(UserBase):
    password: str
