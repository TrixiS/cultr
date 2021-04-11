import sqlalchemy

metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, autoincrement=True),
    sqlalchemy.Column("username", sqlalchemy.String, unique=True),
    sqlalchemy.Column("hashed_password", sqlalchemy.String)
)

sessions = sqlalchemy.Table(
    "sessions",
    metadata,
    sqlalchemy.Column("username", sqlalchemy.String,
                      sqlalchemy.ForeignKey("users.username")),
    sqlalchemy.Column("token", sqlalchemy.String)
)

urls = sqlalchemy.Table(
    "urls",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, unique=True,
                      autoincrement=True, primary_key=True),
    sqlalchemy.Column("owner_username", sqlalchemy.String,
                      sqlalchemy.ForeignKey("users.username")),
    sqlalchemy.Column("name", sqlalchemy.String, unique=True),
    sqlalchemy.Column("destination", sqlalchemy.String),
    sqlalchemy.Column("uses", sqlalchemy.Integer, default=0),
    sqlalchemy.Column("max_uses", sqlalchemy.Integer,
                      nullable=True, default=None),
    sqlalchemy.Column("expiration_datetime",
                      sqlalchemy.DateTime, nullable=True)
)
