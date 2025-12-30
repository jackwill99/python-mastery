from __future__ import annotations

import asyncio
from contextlib import AbstractAsyncContextManager, asynccontextmanager, contextmanager
from dataclasses import dataclass
from typing import AsyncIterator, Callable, Iterator, Protocol

# Pro-Tip: Unlike NestJS providers or Flutter's GetIt, Python DI is often lightweight—context managers for lifecycles plus Protocols for typing.


class DBSession(Protocol):
    async def execute(self, query: str, params: dict[str, object] | None = None) -> object: ...


class EmailClient(Protocol):
    async def send(self, to: str, subject: str, body: str) -> None: ...


@dataclass
class FakeDB:
    dsn: str

    async def execute(self, query: str, params: dict[str, object] | None = None) -> object:
        await asyncio.sleep(0.01)
        return {"query": query, "params": params}

    async def close(self) -> None:
        await asyncio.sleep(0)


@dataclass
class FakeEmail:
    api_key: str

    async def send(self, to: str, subject: str, body: str) -> None:
        await asyncio.sleep(0)
        print(f"Email to {to}: {subject}\n{body}")

    async def close(self) -> None:
        await asyncio.sleep(0)


@contextmanager
def override_attr(obj: object, name: str, replacement: object) -> Iterator[None]:
    """Testing helper to override an attribute for the scope of the context."""

    original = getattr(obj, name)
    setattr(obj, name, replacement)
    try:
        yield
    finally:
        setattr(obj, name, original)


@asynccontextmanager
async def lifespan_db(dsn: str) -> AsyncIterator[FakeDB]:
    db = FakeDB(dsn=dsn)
    try:
        yield db
    finally:
        await db.close()


@asynccontextmanager
async def lifespan_email(api_key: str) -> AsyncIterator[FakeEmail]:
    client = FakeEmail(api_key=api_key)
    try:
        yield client
    finally:
        await client.close()


@dataclass
class Container:
    db_factory: Callable[[], AbstractAsyncContextManager[DBSession]]
    email_factory: Callable[[], AbstractAsyncContextManager[EmailClient]]

    @asynccontextmanager
    async def service_scope(self) -> AsyncIterator["Services"]:
        async with self.db_factory() as db, self.email_factory() as email:
            yield Services(db=db, email=email)


@dataclass
class Services:
    db: DBSession
    email: EmailClient

    async def send_welcome(self, user_email: str) -> None:
        await self.db.execute("insert into audit(event) values (:event)", {"event": "welcome_sent"})
        await self.email.send(user_email, "Welcome!", "Thanks for joining.")


async def main() -> None:
    container = Container(
        db_factory=lambda: lifespan_db("postgresql://localhost/app"),
        email_factory=lambda: lifespan_email("test-key"),
    )
    async with container.service_scope() as services:
        await services.send_welcome("cto@example.com")


if __name__ == "__main__":
    asyncio.run(main())

# Pythonic backend problem solved: Declarative lifecycles per request/task without heavy DI frameworks; async context managers guarantee cleanup.
