from pydantic import BaseModel

# TODO: add email


class User(BaseModel):
    id: int
    username: str
    hashed_password: str

    class Config:
        orm_mode = True


# TODO: make username and email optional
class UserIn(BaseModel):
    username: str
    password: str
