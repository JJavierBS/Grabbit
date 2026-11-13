# Single entry points for humans, agents and future CI. Replace each TODO body once the
# stack is chosen; keep output short (quiet reporters, no progress bars).
.PHONY: setup dev test lint fmt

setup:
	@echo "make setup: TODO (see docs/agents/backend.md and frontend.md)"; exit 1

dev:
	@echo "make dev: TODO"; exit 1

test:
	@echo "make test: TODO (see docs/agents/testing.md)"; exit 1

lint:
	@echo "make lint: TODO"; exit 1

# Format only files changed against main, never whole trees.
fmt:
	@echo "make fmt: TODO (run the formatter on: git diff --name-only origin/main...)"; exit 1
