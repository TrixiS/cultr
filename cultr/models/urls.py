import datetime as dt

from pydantic import Field
from typing import Optional

from .base import DBBaseModel

URL_NAME_REGEX = r"([a-zA-Z0-9_]+)"
URL_DEST_REGEX = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"


class UrlIn(DBBaseModel):
    name: str = Field(regex=URL_NAME_REGEX, max_length=50)
    destination: str = Field(regex=URL_DEST_REGEX)
    max_uses: Optional[int] = Field(None, gt=0)
    expiration_datetime: Optional[dt.datetime] = None


class Url(UrlIn):
    id: int
    owner_id: int
    uses: int = 0
