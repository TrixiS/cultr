import datetime as dt

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.params import Depends

from starlette.responses import RedirectResponse
from typing import Optional, List
from sqlalchemy import select, update, delete, or_

from .oauth2 import current_user
from ..models.users import User
from ..models.urls import Url, UrlIn
from ..database import models as db_models, async_session
from ..utils.db import fetch_user

api_router = APIRouter()
redirect_router = APIRouter()


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

    if request.base_url.netloc in url.destination.host:
        raise HTTPException(
            422, f"Destination cant refer to {url.destination.host}")

    if url_name is None or url_name != url.name:
        async with async_session() as session:
            query = select(db_models.Url).where(db_models.Url.name == url.name)
            result = await session.execute(query)
            db_url = result.scalar()

        if db_url is not None:
            raise HTTPException(409, "Url with the same name already exists")

    return url


@api_router.post("/urls", response_model=Url)
async def urls_post(
    *,
    user: User = Depends(current_user),
    url: UrlIn = Depends(is_valid_url),
):
    async with async_session() as session:
        owner = await fetch_user(user.username)
        db_url = db_models.Url(**url.dict(), uses=0, owner_id=owner.id)
        session.add(db_url)
        await session.commit()

    return Url(
        **url.dict(),
        id=db_url.id,
        owner_id=owner.id
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
        select(db_models.Url)
        .filter_by(owner_id=user.id)
        .offset((page - 1) * items)
        .limit(items)
    )

    async with async_session() as session:
        result = await session.execute(urls_select_query)
        return [Url.from_orm(r) for r in result.scalars().all()]


@api_router.get("/urls/{url_name}", response_model=Url)
async def urls_get_single(
    *,
    user: User = Depends(current_user),
    url_name: str
):
    url_select_query = (
        select(db_models.Url)
        .filter_by(owner_id=user.id, name=url_name)
    )

    async with async_session() as session:
        result = await session.execute(url_select_query)
        url = result.scalar()

    if url is None:
        raise HTTPException(404)

    return Url.from_orm(url)


@api_router.delete("/urls/{url_name}", status_code=204)
async def urls_delete(
    *,
    user: User = Depends(current_user),
    url_name: str
):
    url_delete_query = (
        delete(db_models.Url)
        .filter_by(owner_id=user.id, name=url_name)
    )

    async with async_session() as session:
        result = await session.execute(url_delete_query)
        await session.commit()

    if result.rowcount < 1:
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
        update(db_models.Url)
        .filter_by(owner_id=user.id, name=url_name)
        .values(**url.dict())
    )

    async with async_session() as session:
        result = await session.execute(url_update_query)
        await session.commit()

    if result.rowcount < 1:
        raise HTTPException(404, "No data found")

    return Response(status_code=204)


@redirect_router.get("/u/{url_name}")
async def url_redirect_get(url_name: str, request: Request):
    now = dt.datetime.utcnow()

    url_select_query = (
        select(db_models.Url)
        .where(db_models.Url.name == url_name)
        .where(
            or_(
                db_models.Url.max_uses.is_(None),
                db_models.Url.uses < db_models.Url.max_uses
            )
        )
        .where(
            or_(
                db_models.Url.expiration_datetime.is_(None),
                db_models.Url.expiration_datetime > now
            )
        )
    )

    async with async_session() as session:
        select_result = await session.execute(url_select_query)
        db_url = select_result.scalar()

        if db_url is None:
            return RedirectResponse(request.base_url)

        url_update_query = (
            update(db_models.Url)
            .filter_by(name=url_name)
            .values(uses=db_url.uses + 1)
        )

        await session.execute(url_update_query)
        await session.commit()

    return RedirectResponse(db_url.destination)
