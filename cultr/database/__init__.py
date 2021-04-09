import sqlalchemy

from databases import Database

from . import models

# TODO!!!: add CORS

# TODO: check with postgres
DATABASE_URL = "sqlite:///database.db"

database = Database(DATABASE_URL)

# TODO: remove check same thread
#       install postgres
#       delete mysql
#       move database_url into env
engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
models.metadata.create_all(engine)
