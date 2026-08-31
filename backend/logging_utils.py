from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime


_request_logs: ContextVar[list[str] | None] = ContextVar(
    "request_logs",
    default=None,
)


def _format_log(level: str, component: str, message: str) -> str:
    timestamp = datetime.now().astimezone().strftime("%H:%M:%S")
    return f"{timestamp} | {level.upper():<5} | {component.upper():<10} | {message}"


def ingestion_log(message: str) -> None:
    """Write an ingestion message to the backend terminal."""
    print(_format_log("INFO", "INGESTION", message), flush=True)


def workflow_log(
    message: str,
    *,
    component: str = "WORKFLOW",
    level: str = "INFO",
) -> None:
    """Write a workflow message to the console and the current request log."""
    formatted_message = _format_log(level, component, message)
    print(formatted_message, flush=True)
    logs = _request_logs.get()
    if logs is not None:
        logs.append(formatted_message)


@contextmanager
def capture_workflow_logs() -> Iterator[list[str]]:
    """Capture workflow messages without mixing concurrent request logs."""
    logs: list[str] = []
    token = _request_logs.set(logs)
    try:
        yield logs
    finally:
        _request_logs.reset(token)
