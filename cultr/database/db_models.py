import sqlalchemy

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import Column
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    username = Column(sqlalchemy.String, unique=True)
    email = Column(sqlalchemy.String, unique=True)
    email_confirmed = Column(sqlalchemy.Boolean, default=False)
    hashed_password = Column(sqlalchemy.String)


class Url(Base):
    __tablename__ = "urls"

    id = Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    owner_id = Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    name = Column(sqlalchemy.String, unique=True)
    destination = Column(sqlalchemy.String)
    uses = Column(sqlalchemy.Integer, default=0)
    max_uses = Column(sqlalchemy.Integer, nullable=True, default=None)
    expiration_datetime = Column(
        sqlalchemy.DateTime, nullable=True, default=None)

    owner = relationship("User", foreign_keys=[owner_id])
