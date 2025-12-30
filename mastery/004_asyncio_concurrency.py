from __future__ import annotations

import asyncio
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from random import randint
from typing import Iterable

# Pro-Tip: Think Node's worker_threads vs Dart isolates—CPU-bound compression stalls Python threads due to the GIL; multiprocessing sidesteps the GIL for true parallelism.


@dataclass(frozen=True)
class VideoJob:
    video_id: str
    quality: str


async def fetch_metadata(video_id: str) -> dict[str, str]:
    # Simulate I/O-bound metadata fetch (e.g., hitting object storage or a metadata DB).
    await asyncio.sleep(0.05)
    return {"video_id": video_id, "duration_sec": str(randint(30, 600)), "codec": "h264"}


def compress_video(job: VideoJob) -> str:
    # CPU-bound loop to simulate heavy compression work; runs in a separate process to bypass the GIL.
    pixels = 1024 * 512
    _ = sum((i * 3) % 255 for i in range(pixels))  # fake CPU load
    return f"compressed_{job.video_id}_{job.quality}"


async def process_videos(video_ids: Iterable[str], quality: str = "1080p") -> list[str]:
    async with asyncio.TaskGroup() as tg:
        meta_tasks = {tg.create_task(fetch_metadata(v)): v for v in video_ids}
    metadata = {v: t.result() for t, v in meta_tasks.items()}

    # Senior Note: ThreadPoolExecutor would serialize CPU-bound work under the GIL. ProcessPoolExecutor uses OS processes for parallel compression.
    loop = asyncio.get_running_loop()
    results: list[str] = []
    with ProcessPoolExecutor() as pool:
        compression_tasks = [
            loop.run_in_executor(pool, compress_video, VideoJob(video_id=v, quality=quality)) for v in metadata
        ]
        for result in await asyncio.gather(*compression_tasks):
            results.append(result)
    return results


async def main() -> None:
    videos = [f"vid_{i}" for i in range(5)]
    outputs = await process_videos(videos, quality="720p")
    for out in outputs:
        print(out)


if __name__ == "__main__":
    asyncio.run(main())

