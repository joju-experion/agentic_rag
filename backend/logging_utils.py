from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar


_request_logs: ContextVar[list[str] | None] = ContextVar(
    "request_logs",
    default=None,
)


def workflow_log(message: str) -> None:
    """Write a workflow message to the console and the current request log."""
    print(message)
    logs = _request_logs.get()
    if logs is not None:
        logs.append(message)


@contextmanager
def capture_workflow_logs() -> Iterator[list[str]]:
    """Capture workflow messages without mixing concurrent request logs."""
    logs: list[str] = []
    token = _request_logs.set(logs)
    try:
        yield logs
    finally:
        _request_logs.reset(token)
