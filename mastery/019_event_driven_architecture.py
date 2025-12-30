from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Awaitable, Callable

# Pro-Tip: Similar to Node's EventEmitter or Dart Streams; asyncio.Queue + handler registry yields backpressure-friendly event buses.

Handler = Callable[[dict[str, object]], Awaitable[None]]


class EventBus:
    def __init__(self) -> None:
        self.handlers: dict[str, list[Handler]] = defaultdict(list)
        self.queue: asyncio.Queue[tuple[str, dict[str, object]]] = asyncio.Queue()

    def subscribe(self, event: str, handler: Handler) -> None:
        self.handlers[event].append(handler)

    async def publish(self, event: str, payload: dict[str, object]) -> None:
        await self.queue.put((event, payload))

    async def run(self) -> None:
        while True:
            event, payload = await self.queue.get()
            tasks = [asyncio.create_task(h(payload)) for h in self.handlers.get(event, [])]
            if tasks:
                await asyncio.gather(*tasks)
            self.queue.task_done()


async def on_user_created(payload: dict[str, object]) -> None:
    await asyncio.sleep(0.01)
    print("welcome user", payload["user_id"])


async def on_user_created_audit(payload: dict[str, object]) -> None:
    await asyncio.sleep(0.01)
    print("audit user", payload)


async def main() -> None:
    bus = EventBus()
    bus.subscribe("user.created", on_user_created)
    bus.subscribe("user.created", on_user_created_audit)
    runner = asyncio.create_task(bus.run())
    await bus.publish("user.created", {"user_id": "u-1"})
    await bus.queue.join()
    runner.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await runner


if __name__ == "__main__":
    import contextlib

    asyncio.run(main())

# Pythonic backend problem solved: Simple async event bus for decoupled workflows; swap Queue with Kafka or NATS for distributed setups.
