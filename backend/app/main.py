import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.api.errors import install_error_handlers
from app.config import REPO_ROOT
from app.runtime import start_scheduler
from app.store.db import init_db
from app.workspace import WorkspaceMiddleware

FRONTEND_DIST = REPO_ROOT / "frontend" / "dist"

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    init_db()
    jobs = start_scheduler()
    app.state.scheduler = jobs.scheduler
    try:
        yield
    finally:
        jobs.shutdown()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Grabbit API",
        version="0.1.0",
        lifespan=lifespan,
        openapi_url="/api/openapi.json",
        docs_url="/api/docs",
        redoc_url=None,
    )
    install_error_handlers(app)
    app.add_middleware(WorkspaceMiddleware)
    app.include_router(api_router)
    if FRONTEND_DIST.is_dir():
        app.mount("/", StaticFiles(directory=FRONTEND_DIST, html=True), name="frontend")
    return app


app = create_app()
