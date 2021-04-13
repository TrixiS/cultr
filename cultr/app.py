from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config
from .database import database
from .routers import urls, oauth2

app = FastAPI()
app.include_router(oauth2.router, prefix="/api", tags=["oauth"])
app.include_router(urls.api_router, prefix="/api/v1", tags=["urls"])
app.include_router(urls.redirect_router, tags=["urls"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
