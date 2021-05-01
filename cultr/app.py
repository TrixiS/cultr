from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import init_database
from .routers import login, users, urls
from .config import settings

app = FastAPI()
app.include_router(login.router, prefix="/api", tags=["login"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(urls.api_router, prefix="/api/v1/urls", tags=["urls"])
app.include_router(urls.redirect_router, tags=["urls"])

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

@app.on_event("startup")
async def startup():
    await init_database()
