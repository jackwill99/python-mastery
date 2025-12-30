from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator

from sqlalchemy import String, select, text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Pro-Tip: SQLAlchemy 2.0 feels like TypeORM/Prisma but with explicit sessions and composable expressions; async engine maps to PostgreSQL/SQLite without changing models.


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True)
    plan: Mapped[str] = mapped_column(String(32), default="free")


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


async def upsert_user(session: AsyncSession, *, email: str, plan: str) -> User:
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        user.plan = plan
    else:
        user = User(email=email, plan=plan)
        session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def list_users(session: AsyncSession) -> list[User]:
    result = await session.execute(select(User).order_by(User.id))
    return list(result.scalars())


async def raw_health_check(engine: AsyncEngine) -> bool:
    async with engine.connect() as conn:
        await conn.execute(text("select 1"))
    return True


async def main() -> None:
    db = await DB.create("sqlite+aiosqlite:///:memory:")
    try:
        async with db.session() as session:
            await upsert_user(session, email="cto@example.com", plan="pro")
            await upsert_user(session, email="dev@example.com", plan="free")
            users = await list_users(session)
            for user in users:
                print(f"{user.id} {user.email} ({user.plan})")
        print("Health check:", await raw_health_check(db.engine))
    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(main())

# Pythonic backend problem solved: Async ORM with explicit sessions; easy to swap SQLite for PostgreSQL by changing the URL only.
