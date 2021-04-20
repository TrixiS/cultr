from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from . import models
from ..config import settings

# TODO: pydantic HttpUrl
# from pydantic import HttpUrl


engine = create_async_engine(settings.DATABASE_URI, echo=True)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
