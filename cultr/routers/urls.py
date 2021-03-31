import datetime as dt

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.params import Depends
from pydantic import BaseModel, Field
from typing import Optional

from .auth import cookie_auth, Session

from ..database import database
from ..database.models import users, urls

api_router = APIRouter()


class UrlIn(BaseModel):
    name: str
    source: str
    destination: str
    max_uses: Optional[int] = Field(None, gt=0)
    expiration_datetime: Optional[dt.datetime] = None


class Url(UrlIn):
    id: int
    owner_username: str
    uses: int = 0


@api_router.post("/url", response_model=Url)
async def url_post(
    *,
    session: Session = Depends(cookie_auth),
    url: UrlIn,
):
    now = dt.datetime.now()

    if url.expiration_datetime is not None and url.expiration_datetime <= now:
        raise HTTPException(422, "Expiration datetime should be future")

    url_select_query = urls.select().where(urls.c.name == url.name)
    db_url = await database.fetch_one(url_select_query)

    if db_url is not None:
        raise HTTPException(409, "Url with the same name already exists")

    url_insert_query = urls.insert().values(
        **url.dict(),
        owner_username=session.username
    )

    inserted_url_id = await database.execute(url_insert_query)

    return Url(
        **url.dict(),
        id=inserted_url_id,
        owner_username=session.username
    )

# TODO: GET /url/
# TODO: /url/<name: str>
