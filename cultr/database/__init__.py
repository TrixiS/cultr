from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from . import models
from .. import config

# TODO: nginx.conf
# TODO: readme for frontend repo

engine = create_async_engine(config.DATABASE_URI, echo=True)
async_session = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession)


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
