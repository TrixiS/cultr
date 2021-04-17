from sqlalchemy import select

from ..database import async_session
from ..database.models import User


async def fetch_user(username, session=None):
    query = select(User).where(User.username == username)

    if session is None:
        async with async_session() as session_:
            result = await session_.execute(query)
    else:
        result = await session.execute(query)

    return result.scalar()
