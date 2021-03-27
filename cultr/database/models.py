import sqlalchemy

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("username", sqlalchemy.String, unique=True),
    sqlalchemy.Column("hashed_password", sqlalchemy.String)
)

sessions = sqlalchemy.Table(
    "sessions",
    metadata,
    sqlalchemy.Column("username", sqlalchemy.String, sqlalchemy.ForeignKey("users.username")),
    sqlalchemy.Column("token", sqlalchemy.String)
)
