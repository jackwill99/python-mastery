from __future__ import annotations

import logging
import uuid
from contextvars import ContextVar
from dataclasses import dataclass
from typing import Callable, Coroutine

# Pro-Tip: Like OpenTelemetry in Node/Dart, but ContextVars let you propagate trace/span IDs through async code without manual passing.

trace_id_var: ContextVar[str | None] = ContextVar("trace_id", default=None)


def get_trace_id() -> str:
    trace_id = trace_id_var.get()
    if trace_id is None:
        trace_id = uuid.uuid4().hex
        trace_id_var.set(trace_id)
    return trace_id


def with_trace(func: Callable[..., Coroutine[object, object, object]]) -> Callable[..., Coroutine[object, object, object]]:
    async def wrapper(*args, **kwargs):
        trace_id = get_trace_id()
        logging.info("trace start %s", trace_id)
        try:
            return await func(*args, **kwargs)
        finally:
            logging.info("trace end %s", trace_id)

    return wrapper


@dataclass
class TracedService:
    logger: logging.Logger

    @with_trace
    async def fetch_user(self, user_id: str) -> dict[str, str]:
        self.logger.info("fetching user %s", user_id, extra={"trace_id": get_trace_id()})
        return {"user_id": user_id, "status": "ok", "trace_id": get_trace_id()}


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    service = TracedService(logger=logging.getLogger("traced"))
    await service.fetch_user("u-1")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

# Pythonic backend problem solved: Trace IDs propagated via ContextVars; plug into OpenTelemetry exporter later without refactoring business logic.
