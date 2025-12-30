from __future__ import annotations

import cProfile
import pstats
import time
from contextlib import contextmanager
from io import StringIO
from random import randint
from typing import Iterator

# Pro-Tip: Analogous to Node's inspector or Dart DevTools; cProfile + pstats give CPU hotspots without extra deps.


@contextmanager
def profile_block(label: str) -> Iterator[None]:
    profiler = cProfile.Profile()
    profiler.enable()
    start = time.perf_counter()
    try:
        yield
    finally:
        profiler.disable()
        duration = time.perf_counter() - start
        stream = StringIO()
        stats = pstats.Stats(profiler, stream=stream).strip_dirs().sort_stats("cumulative")
        stats.print_stats(5)
        print(f"[profile:{label}] {duration:.3f}s\n{stream.getvalue()}")


def fib(n: int) -> int:
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)


def main() -> None:
    with profile_block("compute"):
        total = sum(fib(randint(20, 24)) for _ in range(5))
    print("total:", total)


if __name__ == "__main__":
    main()

# Pythonic backend problem solved: Quick profiling of hot paths to guide optimization before adding caching or scaling.
