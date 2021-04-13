import sqlalchemy

from databases import Database

from . import models
from .. import config

# TODO: make pytest tests
# TODO: nginx.conf

database = Database(config.DATABASE_URL)

engine = sqlalchemy.create_engine(
    config.DATABASE_URL,
    connect_args=config.DATABASE_CONNECT_ARGS
)

models.metadata.create_all(engine)
