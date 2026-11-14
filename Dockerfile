# syntax=docker/dockerfile:1.7
# Stage 1: build the React app.
FROM node:24-slim AS web
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
# OpenUI sends install telemetry from a postinstall script unless told not to.
ENV DO_NOT_TRACK=1 OPENUI_TELEMETRY_DISABLED=1
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# Stage 2: FastAPI serves the API and frontend/dist from one process.
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.13 /uv /usr/local/bin/uv
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PATH=/app/backend/.venv/bin:$PATH \
    DATABASE_PATH=/app/data/grabbit.db \
    CALA_MODE=replay \
    LLM_MODE=gemini \
    DEMO_MODE=1
WORKDIR /app/backend
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY backend/app ./app
COPY --from=web /app/frontend/dist /app/frontend/dist
# Ship the warmed Cala cache when it exists, so the deployed demo works with CALA_MODE=replay.
RUN --mount=type=bind,target=/ctx \
    mkdir -p /app/data && \
    if [ -f /ctx/data/grabbit.db ]; then cp /ctx/data/grabbit.db /app/data/; fi && \
    useradd --system --uid 1001 grabbit && chown -R grabbit /app/data
USER grabbit
EXPOSE 8000
# deploy/rollout.sh moves traffic only once this reports healthy. The slim image has no curl.
HEALTHCHECK --interval=10s --timeout=3s --start-period=60s --start-interval=2s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)"]
# One worker only: the scheduler lives in the process (architecture.md).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--proxy-headers", "--forwarded-allow-ips", "*"]
