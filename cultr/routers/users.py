from fastapi import APIRouter, Depends, HTTPException, Response, Request, BackgroundTasks

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, or_
from sqlalchemy.exc import IntegrityError

from .. import api_models
from ..config import settings
from ..database import db_models, get_session
from ..utils.security import PASSWORD_CONTEXT, create_jwt_from_data, current_active_user, current_user
from ..utils.email import send_email_confirmation

router = APIRouter()


@router.post("", status_code=201)
async def register(
    *,
    session: AsyncSession = Depends(get_session),
    request: Request,
    user_in: api_models.UserIn,
    background_tasks: BackgroundTasks
):
    user_select_query = select(db_models.User).filter(or_(
        db_models.User.username == user_in.username,
        db_models.User.email == user_in.email
    ))

    result = await session.execute(user_select_query)
    db_user = result.scalar()

    if db_user is not None:
        raise HTTPException(409, "User already exists")

    user = db_models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=PASSWORD_CONTEXT.hash(user_in.password),
        email_confirmed=not settings.EMAILS_ON
    )

    session.add(user)
    await session.commit()

    if settings.EMAILS_ON:
        confirm_jwt = create_jwt_from_data({"sub": user.email})
        confirm_url = str(request.base_url) + f"api/confirm/{confirm_jwt}"
        background_tasks.add_task(
            send_email_confirmation, user.email, confirm_url)

    return Response(status_code=201)


@router.get("/@me", response_model=api_models.User)
async def get_me(current_user: api_models.User = Depends(current_user)):
    return api_models.User.from_orm(current_user)


# TODO: push email into token sub
@router.put("/@me", status_code=201)
async def put_me(
    *,
    session: AsyncSession = Depends(get_session),
    current_user: api_models.User = Depends(current_active_user),
    new_user: api_models.UserUpdate
):
    response = Response(status_code=201)

    if new_user.username == current_user.username and new_user.password is None:
        return response

    if new_user.new_password is not None and not PASSWORD_CONTEXT.verify(
        new_user.password, current_user.hashed_password
    ):
        raise HTTPException(400, "Incorrect original password")

    to_update = {"username": new_user.username}

    if new_user.new_password is not None:
        to_update["hashed_password"] = PASSWORD_CONTEXT.hash(
            new_user.new_password)

    try:
        user_update_query = update(
            db_models.User).filter_by(
            id=current_user.id).values(
            **to_update)

        await session.execute(user_update_query)
    except IntegrityError:
        raise HTTPException(409)

    await session.commit()

    return response
