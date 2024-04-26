from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routers import restaurants

app = FastAPI(
    title="Dish Dispatch",
    version="v1",
    openapi_url="/openapi.json",
    docs_url=None,
    redoc_url="/"
)

app.mount("/static", StaticFiles(directory="api/static", follow_symlink=True), name="static")
app.include_router(restaurants.router)