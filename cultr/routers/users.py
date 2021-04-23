from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm

from ..database import models as db_models, async_session
from ..utils.db import fetch_user
from ..utils.security import PASSWORD_CONTEXT

router = APIRouter()


@router.post("", status_code=201)
async def register(form_data: OAuth2PasswordRequestForm = Depends()):
    async with async_session() as session:
        db_user = await fetch_user(form_data.username, session)

        if db_user is not None:
            raise HTTPException(409, "User already exists")

        user = db_models.User(
            username=form_data.username,
            hashed_password=PASSWORD_CONTEXT.hash(form_data.password)
        )

        session.add(user)
        await session.commit()

    return Response(status_code=201)
