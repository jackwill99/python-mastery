from __future__ import annotations

import json
import logging
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from typing import Iterator

# Pro-Tip: Similar to pino/winston or Dart's Logger, but ContextVars let you thread correlation IDs through async code without globals.

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "msg": record.getMessage(),
            "request_id": request_id_var.get(),
            "logger": record.name,
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def setup_logging() -> logging.Logger:
    logger = logging.getLogger("app")
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger


@contextmanager
def log_context(request_id: str) -> Iterator[None]:
    token = request_id_var.set(request_id)
    try:
        yield
    finally:
        request_id_var.reset(token)


def handle_request(logger: logging.Logger, user_id: str) -> None:
    with log_context(request_id=f"req-{user_id}"):
        logger.info("fetching user profile")
        try:
            raise ValueError("boom")
        except ValueError:
            logger.exception("failed fetching user profile")


if __name__ == "__main__":
    log = setup_logging()
    handle_request(log, "123")

# Pythonic backend problem solved: Structured logs with per-request correlation IDs for observability across async boundaries.
