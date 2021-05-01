from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from starlette.responses import RedirectResponse

from .. import api_models
from ..database import get_session, db_models
from ..utils import security
from ..utils.db import fetch_user

router = APIRouter()


@router.post("/token", response_model=api_models.Token, status_code=201)
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await fetch_user(form_data.username)
    error_400 = HTTPException(400, "Incorrect username or password")

    if db_user is None:
        raise error_400

    if not security.PASSWORD_CONTEXT.verify(
            form_data.password, db_user.hashed_password):
        raise error_400

    token = security.create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/confirm/{confirm_jwt}", status_code=307)
async def confirm(
    *,
    session: AsyncSession = Depends(get_session),
    request: Request,
    confirm_jwt: str
):
    error_404 = HTTPException(404)
    decoded_data = security.decode_jwt(confirm_jwt)

    if decoded_data is None:
        raise error_404

    select_query = select(db_models.User).filter_by(email=decoded_data["sub"])
    result = await session.execute(select_query)
    db_user = result.scalar()

    if db_user is None:
        raise error_404

    db_user.email_confirmed = True
    session.add(db_user)
    await session.commit()

    return RedirectResponse(request.base_url)
