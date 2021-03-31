import uvicorn

from fastapi import FastAPI

from .database import database
from .routers import auth, urls

app = FastAPI()
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(urls.api_router, prefix="/api/v1", tags=["urls"])
# Use /api/v1 for other routers (for urls ofc)

@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


# uvicorn.run("cultr.app:app")