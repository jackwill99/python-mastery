from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from fastapi import Depends, FastAPI

# Pro-Tip: NestJS uses @Injectable + providers; here we stay lightweight with FastAPI Depends and a swappable container for tests.


class DatabaseService(Protocol):
    async def get_balance(self, user_id: str) -> int: ...
    async def debit(self, user_id: str, amount_cents: int) -> None: ...


@dataclass
class RealDatabase(DatabaseService):
    dsn: str

    async def get_balance(self, user_id: str) -> int:
        # Simulate DB call
        return 100_00

    async def debit(self, user_id: str, amount_cents: int) -> None:
        # Simulate update
        return None


@dataclass
class MockDatabase(DatabaseService):
    balances: dict[str, int]

    async def get_balance(self, user_id: str) -> int:
        return self.balances.get(user_id, 0)

    async def debit(self, user_id: str, amount_cents: int) -> None:
        self.balances[user_id] = self.get_balance(user_id) - amount_cents  # type: ignore[assignment]


@dataclass
class Container:
    db: DatabaseService


real_container = Container(db=RealDatabase(dsn="postgresql://localhost/app"))
mock_container = Container(db=MockDatabase(balances={"u-1": 50_00}))


def get_container() -> Container:
    return real_container


app = FastAPI(title="DI Example", version="1.0.0")


@app.get("/balance/{user_id}")
async def balance(user_id: str, container: Container = Depends(get_container)) -> dict[str, int]:
    return {"balance_cents": await container.db.get_balance(user_id)}


@app.post("/debit/{user_id}")
async def debit(user_id: str, amount_cents: int, container: Container = Depends(get_container)) -> dict[str, str]:
    await container.db.debit(user_id, amount_cents)
    return {"status": "ok"}


# Swapping for tests: override dependency in FastAPI test client
def set_mock_container() -> None:
    app.dependency_overrides[get_container] = lambda: mock_container


# Pythonic backend problem solved: Simple container + Depends gives DRY, pluggable services; tests can swap RealDatabase with MockDatabase without touching business logic.
