import sqlalchemy

from databases import Database

from . import models

DATABASE_URL = "sqlite:///database.db"

database = Database(DATABASE_URL)

engine = sqlalchemy.create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
models.metadata.create_all(engine)
