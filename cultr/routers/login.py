from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from .. import api_models
from ..utils.db import fetch_user
from ..utils.security import PASSWORD_CONTEXT, create_access_token

router = APIRouter()


@router.post("/token", response_model=api_models.Token, status_code=201)
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = await fetch_user(form_data.username)
    error_400 = HTTPException(400, "Incorrect username or password")

    if db_user is None:
        raise error_400

    if not PASSWORD_CONTEXT.verify(
            form_data.password, db_user.hashed_password):
        raise error_400

    token = create_access_token({"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}
