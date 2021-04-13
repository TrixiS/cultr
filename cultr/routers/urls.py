import datetime as dt

from fastapi import APIRouter, HTTPException, Request, Response, Query
from fastapi.params import Depends

from starlette.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from sqlalchemy import or_

from .oauth2 import User, current_user

from ..database import database
from ..database.models import urls

URL_NAME_REGEX = r"([a-zA-Z0-9_]+)"
URL_DEST_REGEX = r"https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+"

api_router = APIRouter()
redirect_router = APIRouter()


class UrlIn(BaseModel):
    name: str = Field(regex=URL_NAME_REGEX, max_length=50)
    destination: str = Field(regex=URL_DEST_REGEX)
    max_uses: Optional[int] = Field(None, gt=0)
    expiration_datetime: Optional[dt.datetime] = None


class Url(UrlIn):
    id: int
    owner_username: str
    uses: int = 0


def items_per_page(items: Optional[int] = 25):
    VALID_VALUES = (10, 25, 50, 100)

    if items not in VALID_VALUES:
        raise HTTPException(
            422, f"Items per page value should be in {VALID_VALUES}")

    return items


async def is_valid_url(
    *,
    url: UrlIn,
    url_name: Optional[str] = None,
    request: Request
) -> UrlIn:
    if url.expiration_datetime is not None:
        now = dt.datetime.utcnow()
        expiration_datetime = dt.datetime.utcfromtimestamp(
            url.expiration_datetime.timestamp())

        if now >= expiration_datetime:
            raise HTTPException(422, "Expiration datetime should be future")

    if str(request.base_url) in url.destination:
        raise HTTPException(
            422, f"Link destination can not refer to {url.destination}")

    if url_name is None or url_name != url.name:
        url_select_query = urls.select().where(urls.c.name == url.name)
        db_url = await database.fetch_one(url_select_query)

        if db_url is not None:
            raise HTTPException(409, "Url with the same name already exists")

    return url


@api_router.post("/urls", response_model=Url)
async def urls_post(
    *,
    user: User = Depends(current_user),
    url: UrlIn = Depends(is_valid_url),
):
    url_insert_query = urls.insert().values(
        **url.dict(),
        uses=0,
        owner_username=user.username
    )

    inserted_url_id = await database.execute(url_insert_query)

    return Url(
        **url.dict(),
        id=inserted_url_id,
        owner_username=user.username
    )


@api_router.get("/urls", response_model=List[Url])
async def urls_get_all(
    *,
    user: User = Depends(current_user),
    page: Optional[int] = 1,
    items: Optional[int] = Depends(items_per_page)
):
    if page <= 0:
        page = 1

    urls_select_query = (
        urls.select()
        .where(urls.c.owner_username == user.username)
        .offset((page - 1) * items)
        .limit(items)
    )

    return await database.fetch_all(urls_select_query)


@api_router.get("/urls/{url_name}", response_model=Url)
async def urls_get_single(
    *,
    user: User = Depends(current_user),
    url_name: str
):
    url_select_query = (
        urls.select()
        .where(urls.c.owner_username == user.username)
        .where(urls.c.name == url_name)
    )

    url = await database.fetch_one(url_select_query)

    if url is None:
        raise HTTPException(404)

    return url


@api_router.delete("/urls/{url_name}", status_code=204)
async def urls_delete(
    *,
    user: User = Depends(current_user),
    url_name: str
):
    url_delete_query = (
        urls.delete()
        .where(urls.c.owner_username == user.username)
        .where(urls.c.name == url_name)
    )

    deleted_rows = await database.execute(url_delete_query)

    if deleted_rows < 1:
        raise HTTPException(404, "No data found")

    return Response(status_code=204)


@api_router.put("/urls/{url_name}", status_code=204)
async def urls_put(
    *,
    user: User = Depends(current_user),
    url_name: str,
    url: UrlIn = Depends(is_valid_url)
):
    url_update_query = (
        urls.update()
        .values(**url.dict())
        .where(urls.c.owner_username == user.username)
        .where(urls.c.name == url_name)
    )

    updated_rows = await database.execute(url_update_query)

    if updated_rows < 1:
        raise HTTPException(404, "No data found")

    return Response(status_code=204)


@redirect_router.get("/u/{url_name}")
async def url_redirect_get(url_name: str, request: Request):
    now = dt.datetime.utcnow()

    url_select_query = (
        urls.select()
        .where(urls.c.name == url_name)
        .where(or_(urls.c.max_uses.is_(None), urls.c.uses < urls.c.max_uses))
        .where(or_(urls.c.expiration_datetime.is_(None), urls.c.expiration_datetime > now))
    )

    db_url = await database.fetch_one(url_select_query)

    if db_url is None:
        return RedirectResponse(request.base_url)

    url_update_query = urls.update().where(urls.c.name == url_name).values(
        uses=db_url.uses + 1
    )

    await database.execute(url_update_query)
    return RedirectResponse(db_url.destination)
