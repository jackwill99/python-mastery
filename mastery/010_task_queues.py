from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable

# Pro-Tip: This mirrors BullMQ/Rabbit consumers or Dart isolates; asyncio.Queue gives in-process reliability with backpressure and graceful shutdown.

JobHandler = Callable[[dict[str, object]], Awaitable[None]]


@dataclass
class TaskQueue:
    queue: asyncio.Queue[dict[str, object]]
    handler: JobHandler
    shutdown_event: asyncio.Event

    @classmethod
    def create(cls, handler: JobHandler) -> "TaskQueue":
        return cls(queue=asyncio.Queue(), handler=handler, shutdown_event=asyncio.Event())

    async def publish(self, payload: dict[str, object]) -> None:
        await self.queue.put(payload)

    async def worker(self) -> None:
        while not (self.shutdown_event.is_set() and self.queue.empty()):
            try:
                payload = await asyncio.wait_for(self.queue.get(), timeout=0.5)
            except asyncio.TimeoutError:
                continue
            try:
                await self.handler(payload)
            finally:
                self.queue.task_done()

    async def stop(self) -> None:
        self.shutdown_event.set()
        await self.queue.join()


async def email_handler(job: dict[str, object]) -> None:
    await asyncio.sleep(0.01)
    print(f"sent email to {job['to']} about {job['subject']}")


async def main() -> None:
    queue = TaskQueue.create(email_handler)
    worker_task = asyncio.create_task(queue.worker())
    for i in range(5):
        await queue.publish({"to": f"user{i}@example.com", "subject": "hello"})
    await queue.stop()
    worker_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await worker_task


if __name__ == "__main__":
    import contextlib

    asyncio.run(main())

# Pythonic backend problem solved: In-process, awaitable job handling with graceful shutdown—swap the Queue for Redis/Kafka producer/consumer to scale out.
