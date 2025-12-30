from __future__ import annotations

import asyncio
import contextlib
import functools
import inspect
import threading
import time
from typing import Any, AsyncIterator, Callable, TypeVar

# Pro-Tip: Like NestJS/Dart annotations, decorators wrap behavior; Python adds context managers to scope resources (files, locks, spans) with `with`/`async with`.

R = TypeVar("R")
F = TypeVar("F", bound=Callable[..., Any])


class Span(contextlib.AbstractContextManager["Span"]):
    def __init__(self, name: str) -> None:
        self.name = name
        self.start: float | None = None
        self.duration_ms: float | None = None

    def __enter__(self) -> "Span":
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.duration_ms = (time.perf_counter() - (self.start or 0)) * 1000
        print(f"[span] {self.name} took {self.duration_ms:.2f}ms")
        return False


def timed(span_name: str) -> Callable[[F], F]:
    """Decorator that times sync or async functions without duplicating logic."""

    def decorator(fn: F) -> F:
        if inspect.iscoroutinefunction(fn):

            @functools.wraps(fn)
            async def async_wrapper(*args, **kwargs):
                with Span(span_name):
                    return await fn(*args, **kwargs)

            return async_wrapper  # type: ignore[return-value]

        @functools.wraps(fn)
        def sync_wrapper(*args, **kwargs):
            with Span(span_name):
                return fn(*args, **kwargs)

        return sync_wrapper  # type: ignore[return-value]

    return decorator


def ttl_cache(ttl_seconds: float) -> Callable[[Callable[..., R]], Callable[..., R]]:
    """Cache decorator with per-key TTL, thread-safe for simple workloads."""

    def decorator(fn: Callable[..., R]) -> Callable[..., R]:
        cache: dict[tuple[Any, ...], tuple[float, R]] = {}
        lock = threading.Lock()

        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> R:
            key = args + tuple(sorted(kwargs.items()))
            now = time.monotonic()
            with lock:
                if key in cache:
                    expires_at, value = cache[key]
                    if now < expires_at:
                        return value
                value = fn(*args, **kwargs)
                cache[key] = (now + ttl_seconds, value)
                return value

        return wrapper

    return decorator


@contextlib.asynccontextmanager
async def temporary_flag(flag_name: str) -> AsyncIterator[None]:
    """Async context manager that scopes a feature flag to a block."""

    print(f"flag {flag_name}=on")
    try:
        yield
    finally:
        print(f"flag {flag_name}=off")


@timed("expensive-sync")
@ttl_cache(ttl_seconds=1.0)
def expensive_sync(x: int) -> int:
    time.sleep(0.05)
    return x * 2


@timed("expensive-async")
async def expensive_async(x: int) -> int:
    await asyncio.sleep(0.05)
    return x * 3


if __name__ == "__main__":
    print("sync calls:", [expensive_sync(2) for _ in range(3)])
    asyncio.run(expensive_async(3))

    async def _demo_flag() -> None:
        async with temporary_flag("beta-feature"):
            await asyncio.sleep(0.01)

    asyncio.run(_demo_flag())

# Pythonic backend problem solved: Reusable decorators that handle both sync/async functions and TTL caching; context managers scope feature flags/spans without manual try/finally.
