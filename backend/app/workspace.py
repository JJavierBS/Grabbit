"""Anonymous workspace per browser, so visitors of the deployed demo never share state.

No login (decisions.md): the frontend keeps a random id in `localStorage` and sends it as the
`X-Workspace` header, or as `?workspace=` on the SSE stream, which cannot carry headers.
Requests without one use `default`, which is the laptop demo, the tests and `make dev`.
Stores read `current()`; Cala data stays shared because it is the same for everyone.
"""

import re
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from urllib.parse import parse_qs

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.models import ErrorDetail, ErrorResponse

DEFAULT = "default"
HEADER = "x-workspace"
QUERY = "workspace"

_VALID = re.compile(r"[A-Za-z0-9_-]{1,64}")
_current: ContextVar[str] = ContextVar("workspace", default=DEFAULT)


def current() -> str:
    return _current.get()


@contextmanager
def use(workspace: str) -> Iterator[None]:
    """Run a block as `workspace`: scheduler jobs looping over every visitor."""
    token = _current.set(workspace)
    try:
        yield
    finally:
        _current.reset(token)


def parse(raw: str | None) -> str:
    """The workspace named by the client, `default` when absent; ValueError when malformed."""
    if raw is None or raw == "":
        return DEFAULT
    if not _VALID.fullmatch(raw):
        raise ValueError(raw)
    return raw


def _requested(scope: Scope) -> str | None:
    for name, value in scope.get("headers", []):
        if name.decode("latin-1") == HEADER:
            return value.decode("latin-1")
    values = parse_qs(scope.get("query_string", b"").decode("latin-1")).get(QUERY)
    return values[0] if values else None


class WorkspaceMiddleware:
    """Pure ASGI, so the value is set in the task that also streams SSE responses."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        try:
            workspace = parse(_requested(scope))
        except ValueError:
            detail = ErrorDetail(
                code="invalid_workspace",
                message="The workspace id must be 1-64 letters, digits, '-' or '_'.",
            )
            response = JSONResponse(ErrorResponse(error=detail).model_dump(), status_code=400)
            await response(scope, receive, send)
            return
        with use(workspace):
            await self.app(scope, receive, send)
