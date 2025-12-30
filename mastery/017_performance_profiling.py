from __future__ import annotations

import cProfile
import functools
import time
from functools import lru_cache
from typing import Callable

# Senior Pro-Tip: Like Node's inspector or Dart DevTools, combine cProfile for CPU hotspots with py-spy for low-overhead sampling in prod-like runs.


def timed(fn: Callable[..., object]) -> Callable[..., object]:
    @functools.wraps(fn)
    def wrapper(*args: object, **kwargs: object) -> object:
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} took {time.perf_counter() - start:.4f}s")
        return result

    return wrapper


def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)


@lru_cache(maxsize=256)
def fib_cached(n: int) -> int:
    if n <= 1:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)


def profile_func(fn: Callable[..., object], *args: object, **kwargs: object) -> None:
    profiler = cProfile.Profile()
    profiler.enable()
    fn(*args, **kwargs)
    profiler.disable()
    profiler.print_stats(sort="cumulative")


@timed
def run_unoptimized() -> None:
    fib(32)


@timed
def run_optimized() -> None:
    fib_cached(32)


if __name__ == "__main__":
    print("== Profiling unoptimized ==")
    profile_func(run_unoptimized)
    print("\n== Profiling optimized ==")
    profile_func(run_optimized)
    print("Note: Use `py-spy record -o profile.svg -- python mastery/017_performance_profiling.py` for sampling without code changes.")

