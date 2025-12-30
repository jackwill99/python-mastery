from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator, Iterable

from sqlalchemy import ForeignKey, String, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# Senior Pro-Tip: This maps to Node Prisma/TypeORM or Dart's ORM wrappers, but SQLAlchemy's explicit sessions + async engine give finer control over transactions and connection pooling.


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan", lazy="selectin"
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    amount_cents: Mapped[int] = mapped_column(nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    user: Mapped[User] = relationship(back_populates="transactions")


@dataclass
class DB:
    engine: AsyncEngine
    sessionmaker: async_sessionmaker[AsyncSession]

    @classmethod
    async def create(cls, url: str) -> "DB":
        engine = create_async_engine(url, echo=False)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return cls(engine=engine, sessionmaker=async_sessionmaker(engine, expire_on_commit=False))

    async def session(self) -> AsyncIterator[AsyncSession]:
        async with self.sessionmaker() as session:
            yield session

    async def close(self) -> None:
        await self.engine.dispose()


class UserRepository:
    """Repository decouples ORM from business logic."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email: str) -> User:
        user = User(email=email)
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_with_transactions(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def bulk_insert(self, user: User, txns: Iterable[tuple[int, str]]) -> list[Transaction]:
        records = [Transaction(user=user, amount_cents=amount, currency=currency) for amount, currency in txns]
        self.session.add_all(records)
        await self.session.flush()
        return records

    async def list_by_user(self, user_id: int) -> list[Transaction]:
        result = await self.session.execute(select(Transaction).where(Transaction.user_id == user_id))
        return list(result.scalars())


async def demo() -> None:
    db = await DB.create("sqlite+aiosqlite:///:memory:")
    try:
        async for session in db.session():
            user_repo = UserRepository(session)
            txn_repo = TransactionRepository(session)

            user = await user_repo.create(email="founder@example.com")
            await txn_repo.bulk_insert(user, [(5000, "USD"), (1250, "USD")])
            await session.commit()

            fetched = await user_repo.get_with_transactions(user.id)
            if fetched:
                print(f"User {fetched.email} has {len(fetched.transactions)} txns")
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(demo())

# Production considerations: use pooled DB URLs, handle retries on transient errors, and keep repositories slim to avoid leaking ORM types into service layers.
