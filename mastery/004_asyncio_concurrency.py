from __future__ import annotations

import asyncio
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from math import sqrt
from typing import Iterable

# Pro-Tip: The GIL limits CPU-bound threading (unlike Node's libuv offloading or Dart isolates); use multiprocessing for CPU and asyncio for I/O.


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for i in range(2, int(sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


def count_primes(values: Iterable[int]) -> int:
    return sum(1 for v in values if is_prime(v))


def io_bound_task(delay_ms: int) -> str:
    time.sleep(delay_ms / 1000)
    return f"slept {delay_ms}ms"


async def asyncio_io_workload(delays: list[int]) -> list[str]:
    async def sleeper(d: int) -> str:
        await asyncio.sleep(d / 1000)
        return f"async slept {d}ms"

    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(sleeper(d)) for d in delays]
    return [t.result() for t in tasks]


def threaded_io(delays: list[int]) -> list[str]:
    with ThreadPoolExecutor(max_workers=4) as pool:
        return list(pool.map(io_bound_task, delays))


def threaded_cpu(values: list[int]) -> int:
    with ThreadPoolExecutor(max_workers=4) as pool:
        return sum(pool.map(is_prime, values))  # GIL keeps this mostly single-core


def multiprocess_cpu(values: list[int]) -> int:
    with ProcessPoolExecutor() as pool:
        return sum(pool.map(is_prime, values))


def main() -> None:
    nums = list(range(100_000, 100_800))
    delays = [50, 60, 70, 80]

    start = time.perf_counter()
    threaded_cpu_result = threaded_cpu(nums)
    print(f"Threaded CPU primes={threaded_cpu_result} took {time.perf_counter() - start:.3f}s")

    start = time.perf_counter()
    multiprocess_cpu_result = multiprocess_cpu(nums)
    print(f"Multiprocess CPU primes={multiprocess_cpu_result} took {time.perf_counter() - start:.3f}s")

    start = time.perf_counter()
    threaded_io_result = threaded_io(delays)
    print(f"Threaded IO: {threaded_io_result} took {time.perf_counter() - start:.3f}s")

    start = time.perf_counter()
    asyncio_result = asyncio.run(asyncio_io_workload(delays))
    print(f"AsyncIO IO: {asyncio_result} took {time.perf_counter() - start:.3f}s")


if __name__ == "__main__":
    main()
