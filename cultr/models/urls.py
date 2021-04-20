import datetime as dt

from pydantic import BaseModel, Field, HttpUrl
from typing import Optional

URL_NAME_REGEX = r"([a-zA-Z0-9_]+)"
URL_DEST_REGEX = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"


class UrlIn(BaseModel):
    name: str = Field(regex=URL_NAME_REGEX, max_length=50)
    destination: HttpUrl
    max_uses: Optional[int] = Field(None, gt=0)
    expiration_datetime: Optional[dt.datetime] = None


class Url(UrlIn):
    id: int
    owner_id: int
    uses: int = 0

    class Config:
        orm_mode = True
