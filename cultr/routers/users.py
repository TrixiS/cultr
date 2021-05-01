from fastapi import APIRouter, Depends, HTTPException, Response, Request, BackgroundTasks

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from .. import api_models
from ..database import db_models, get_session
from ..utils.security import PASSWORD_CONTEXT, create_jwt_from_data
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
        hashed_password=PASSWORD_CONTEXT.hash(user_in.password)
    )

    session.add(user)
    await session.commit()

    confirm_jwt = create_jwt_from_data({"sub": user.email})
    confirm_url = str(request.base_url) + f"api/confirm/{confirm_jwt}"
    background_tasks.add_task(send_email_confirmation, user.email, confirm_url)

    return Response(status_code=201)
