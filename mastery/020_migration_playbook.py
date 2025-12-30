from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Sequence

# Pro-Tip: Similar to Prisma/Alembic migrations with feature flags; Python favors idempotent, forward-only steps plus shadow writes to avoid downtime.


@dataclass
class MigrationStep:
    name: str
    sql: str
    flag: str | None = None  # optional feature flag to guard rollout


async def apply_step(step: MigrationStep) -> None:
    print(f"applying migration: {step.name}")
    await asyncio.sleep(0.01)  # simulate DB execution
    if step.flag:
        print(f"toggle on feature flag: {step.flag}")


async def run_migrations(steps: Sequence[MigrationStep]) -> None:
    for step in steps:
        await apply_step(step)
    print("all migrations applied")


def plan_zero_downtime() -> list[MigrationStep]:
    return [
        MigrationStep(name="add_new_column_nullable", sql="alter table users add column tier text null"),
        MigrationStep(
            name="backfill_column",
            sql="update users set tier = 'free' where tier is null",
        ),
        MigrationStep(
            name="set_not_null",
            sql="alter table users alter column tier set not null",
        ),
        MigrationStep(
            name="dual_writes",
            sql="-- application writes both old and new columns under feature flag",
            flag="dual_writes",
        ),
        MigrationStep(
            name="cleanup_old_column",
            sql="alter table users drop column legacy_plan",
        ),
    ]


async def main() -> None:
    steps = plan_zero_downtime()
    await run_migrations(steps)


if __name__ == "__main__":
    asyncio.run(main())

# Pythonic backend problem solved: Sequenced, idempotent migrations with optional feature flags for dual writes/backfills to avoid downtime.
