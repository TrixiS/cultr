from typing import Generator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from . import db_models
from ..config import settings


engine = create_async_engine(settings.DATABASE_URI, echo=True)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(db_models.Base.metadata.create_all)


async def get_session() -> Generator:
    try:
        session = async_session()
        yield session
    finally:
        await session.close()
