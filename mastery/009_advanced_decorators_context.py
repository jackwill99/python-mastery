from __future__ import annotations

import contextlib
import random
import time
from collections.abc import Callable, Generator
from typing import ParamSpec, TypeVar

# Senior Pro-Tip: Similar to Node retry middleware or Dart zones, decorators/context managers in Python let you wrap behavior without touching call sites; use them to standardize reliability and resource handling.

P = ParamSpec("P")
R = TypeVar("R")


def retry(
    attempts: int = 3,
    base_delay: float = 0.05,
    jitter: float = 0.02,
    retry_for: tuple[type[Exception], ...] = (Exception,),
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            last_exc: Exception | None = None
            for i in range(attempts):
                try:
                    return fn(*args, **kwargs)
                except retry_for as exc:
                    last_exc = exc
                    delay = base_delay * (2**i) + random.uniform(0, jitter)
                    time.sleep(delay)
            raise last_exc if last_exc else RuntimeError("retry failed with no exception captured")

        return wrapper

    return decorator


@contextlib.contextmanager
def atomic_transaction(conn: "DBConnection") -> Generator["DBConnection", None, None]:
    """Context manager to scope a transaction; ensures rollback on failure."""

    conn.begin()
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    else:
        conn.commit()


class DBConnection:
    """Minimal DB connection stub for demo purposes."""

    def __init__(self) -> None:
        self._in_txn = False

    def begin(self) -> None:
        self._in_txn = True
        print("BEGIN")

    def commit(self) -> None:
        self._in_txn = False
        print("COMMIT")

    def rollback(self) -> None:
        self._in_txn = False
        print("ROLLBACK")

    def execute(self, sql: str) -> None:
        if not self._in_txn:
            raise RuntimeError("must be in transaction")
        print(f"SQL> {sql}")


@retry(attempts=4, base_delay=0.05, retry_for=(ConnectionError,))
def flaky_call(endpoint: str) -> str:
    if random.random() < 0.7:
        raise ConnectionError("temporary network issue")
    return f"ok:{endpoint}"


def demo() -> None:
    conn = DBConnection()
    try:
        with atomic_transaction(conn) as c:
            c.execute("insert into payments values (1, 1000)")
            print(flaky_call("https://payments.example.com"))
    except Exception as exc:
        print("operation failed:", exc)


if __name__ == "__main__":
    demo()

# Production considerations: integrate retries with logging/metrics; avoid retrying non-idempotent operations unless guarded. For atomic contexts, use your DB driver/ORM transaction APIs instead of this stub.
