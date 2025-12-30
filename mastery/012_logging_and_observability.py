from __future__ import annotations

import structlog
from contextvars import ContextVar
from typing import Any, Callable

# Senior Pro-Tip: Like pino/winston with CLS in Node or Logger with zones in Dart, structlog + ContextVars propagate correlation IDs cleanly through async code.

correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def add_correlation_id(logger: structlog.types.WrappedLogger, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    cid = correlation_id.get()
    if cid:
        event_dict["correlation_id"] = cid
    return event_dict


def configure_logger() -> structlog.stdlib.BoundLogger:
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            add_correlation_id,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(structlog.INFO),
    )
    return structlog.get_logger()


def with_correlation_id(cid: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            token = correlation_id.set(cid)
            try:
                return fn(*args, **kwargs)
            finally:
                correlation_id.reset(token)

        return wrapper

    return decorator


logger = configure_logger()


@with_correlation_id("req-123")
def handle_request() -> None:
    logger.info("processing", path="/payments", method="POST")
    logger.info("completed", status=200)


if __name__ == "__main__":
    handle_request()

