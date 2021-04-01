from dotenv import load_dotenv
from pathlib import Path

from fastapi import FastAPI

from .database import database
from .routers import urls, oauth2

load_dotenv(Path(__file__).parent.parent / ".env")

app = FastAPI()
app.include_router(oauth2.router, prefix="/api", tags=["oauth"])
app.include_router(urls.api_router, prefix="/api/v1", tags=["urls"])
app.include_router(urls.redirect_router, tags=["urls"])


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
