import os
from fastapi.testclient import TestClient

os.environ["DATABASE_URI"] = "sqlite+aiosqlite:///database.db"  # noqa

from ..app import app

client = TestClient(app)
