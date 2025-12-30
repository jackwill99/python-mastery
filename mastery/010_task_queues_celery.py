from __future__ import annotations

"""
Distributed task architecture using Celery + Redis.
Senior Pro-Tip: Comparable to Node BullMQ (Redis broker) or Dart's work queues; Celery separates broker (message transport) from result backend (state store).
"""

from celery import Celery

# Broker: where tasks are queued (e.g., Redis). Result backend: where task states/results live.
app = Celery(
    "payments",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/1",
)

app.conf.update(
    task_routes={"tasks.process_payment": {"queue": "payments"}},
    task_acks_late=True,  # ensure tasks are re-queued on worker crash
    worker_prefetch_multiplier=1,  # fair dispatch for long-running tasks
)


@app.task(bind=True, autoretry_for=(ConnectionError,), retry_backoff=True, max_retries=5)
def process_payment(self, user_id: str, amount_cents: int) -> str:
    # Simulate calling an external gateway
    if amount_cents <= 0:
        raise ValueError("invalid amount")
    return f"paid:{user_id}:{amount_cents}"


@app.task
def send_receipt(user_email: str, transaction_id: str) -> str:
    return f"receipt:{user_email}:{transaction_id}"


if __name__ == "__main__":
    # Example enqueue (normally from FastAPI view):
    result = process_payment.delay("u-1", 2500)
    print("Queued payment:", result.id)
    # To chain: process_payment.s(... ) | send_receipt.s(...)
