# Single entry points for humans, agents and CI. Keep output short.
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
.PHONY: setup dev test lint fmt warm gen-api docker deploy

BASE = $(shell git merge-base origin/main HEAD 2>/dev/null || echo HEAD)
CHANGED = $(shell { git diff --name-only --diff-filter=ACMR $(BASE); \
	git ls-files --others --exclude-standard; } | sort -u)
CHANGED_PY = $(patsubst backend/%,%,$(filter backend/%.py,$(CHANGED)))
CHANGED_WEB = $(patsubst frontend/%,%,$(filter-out frontend/src/api/schema.ts frontend/package-lock.json,\
	$(filter frontend/%.ts frontend/%.tsx frontend/%.js frontend/%.json frontend/%.css,$(CHANGED))))

setup:
	cd backend && uv sync --quiet
	cd frontend && DO_NOT_TRACK=1 OPENUI_TELEMETRY_DISABLED=1 npm ci --silent --no-audit --no-fund
	bash scripts/setup.sh

# API on :8000 (one worker, see architecture.md) and Vite on :5173 proxying /api.
dev:
	@trap 'trap - INT TERM EXIT; kill -TERM 0 2>/dev/null' INT TERM EXIT; \
	(cd backend && uv run uvicorn app.main:app --reload --port 8000) & \
	(cd frontend && npm run --silent dev) & \
	wait

test:
	cd backend && uv run pytest -q
	cd frontend && npm run --silent test

lint:
	cd backend && uv run ruff check --quiet . && uv run ruff format --check --quiet .
	cd frontend && npx biome check --error-on-warnings . && npx tsc -b

# Format only files changed on this branch (committed or not), never whole trees.
fmt:
	@if [ -n "$(CHANGED_PY)" ]; then cd backend && uv run ruff check --quiet --fix --select I $(CHANGED_PY) && uv run ruff format --quiet $(CHANGED_PY); fi
	@if [ -n "$(CHANGED_WEB)" ]; then cd frontend && npx biome check --write --no-errors-on-unmatched $(CHANGED_WEB); fi
	@echo "fmt: $(words $(CHANGED_PY)) python, $(words $(CHANGED_WEB)) web file(s)"

# Fills the Cala cache for the event and the demo path; e.g. make warm ARGS="--limit 150".
warm:
	cd backend && uv run $$([ -f ../.env ] && echo --env-file ../.env) python -m scripts.warm $(ARGS)

# Regenerates frontend/src/api/schema.ts; needs the API running on :8000.
gen-api:
	cd frontend && npm run --silent gen:api

# Checkpoints the SQLite WAL first so the image ships a complete warmed cache.
docker:
	@if [ -f data/grabbit.db ]; then cd backend && uv run python -c \
		"import sqlite3; sqlite3.connect('../data/grabbit.db').execute('PRAGMA wal_checkpoint(TRUNCATE)')"; fi
	docker build --platform linux/amd64 -t grabbit .

# Builds, pushes and deploys to AWS Lightsail (README "Deploy").
deploy:
	bash scripts/deploy.sh
