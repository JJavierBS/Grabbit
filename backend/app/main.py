from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import chat, errors, profile, reports
from app.config import get_settings
from app.store import chat as _chat_tables  # noqa: F401  registers tables
from app.store import db
from app.store import profile as _profile_tables  # noqa: F401
from app.store import reports as _report_tables  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    db.init_db()
    yield
    db.close()


app = FastAPI(title="Grabbit", lifespan=lifespan, openapi_url="/api/openapi.json")
errors.install(app)
app.include_router(profile.router)
app.include_router(chat.router)
app.include_router(reports.router)


@app.get("/api/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {"status": "ok", "cala_mode": settings.cala_mode, "llm_mode": settings.llm_mode}
