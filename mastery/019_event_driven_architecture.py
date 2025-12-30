from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Awaitable, Callable

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

# Senior Pro-Tip: Comparable to Node KafkaJS or Dart Streams; enforce idempotency to avoid double-processing when consumers restart or rebalances occur.

Handler = Callable[[dict[str, object]], Awaitable[None]]


class EventBus:
    def __init__(self, producer: AIOKafkaProducer) -> None:
        self.producer = producer

    async def publish(self, topic: str, payload: dict[str, object]) -> None:
        await self.producer.send_and_wait(topic, str(payload).encode())


class Consumer:
    def __init__(self, topic: str, group_id: str, bootstrap: str = "localhost:9092") -> None:
        self.topic = topic
        self.group_id = group_id
        self.bootstrap = bootstrap
        self.handlers: dict[str, list[Handler]] = defaultdict(list)
        self.processed_keys: set[str] = set()

    def on(self, event: str, handler: Handler) -> None:
        self.handlers[event].append(handler)

    async def start(self) -> None:
        consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap,
            group_id=self.group_id,
            enable_auto_commit=True,
        )
        await consumer.start()
        try:
            async for msg in consumer:
                key = f"{msg.topic}:{msg.partition}:{msg.offset}"
                if key in self.processed_keys:
                    continue  # idempotent guard
                self.processed_keys.add(key)
                event_name = self.topic
                payload = {"value": msg.value.decode()}
                for handler in self.handlers.get(event_name, []):
                    await handler(payload)
        finally:
            await consumer.stop()


async def example_handler(payload: dict[str, object]) -> None:
    print("handled:", payload)


async def main() -> None:
    producer = AIOKafkaProducer(bootstrap_servers="localhost:9092")
    await producer.start()
    bus = EventBus(producer)
    consumer = Consumer(topic="user.created", group_id="payments")
    consumer.on("user.created", example_handler)
    consumer_task = asyncio.create_task(consumer.start())
    await bus.publish("user.created", {"user_id": "u-1"})
    await asyncio.sleep(0.5)
    consumer_task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await consumer_task
    await producer.stop()


if __name__ == "__main__":
    import contextlib

    asyncio.run(main())

