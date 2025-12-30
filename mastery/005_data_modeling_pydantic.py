from __future__ import annotations

import sys
from datetime import datetime
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

# Pro-Tip: Pydantic V2 plays the role of NestJS DTOs or Dart freezed models, but with high-performance parsing and optional `__slots__` to reduce memory.

UserPlan = Literal["free", "pro", "enterprise"]
NonEmptyStr = Annotated[str, Field(min_length=1, max_length=128)]
Tag = Annotated[str, Field(min_length=1, max_length=32)]


class UserProfile(BaseModel):
    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
        slots=True,  # Pydantic slots to reduce per-instance memory
    )

    user_id: NonEmptyStr
    email: EmailStr
    plan: UserPlan = "free"
    tags: list[Tag] = Field(default_factory=list, max_length=20)
    seats: int | None = Field(default=None, ge=1, le=10_000)
    company: str | None = Field(default=None, max_length=140)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @model_validator(mode="after")
    def validate_plan_contracts(self) -> "UserProfile":
        # Cross-field rule: enterprise requires company + seats
        if self.plan == "enterprise":
            if not self.company:
                raise ValueError("enterprise plan requires company name")
            if not self.seats:
                raise ValueError("enterprise plan requires seats")
        return self


class SlimProfile:
    """Memory-lean profile using __slots__ (avoids per-instance __dict__)."""

    __slots__ = ("user_id", "email", "plan", "tags")

    def __init__(self, user_id: str, email: str, plan: UserPlan, tags: list[str]):
        self.user_id = user_id
        self.email = email
        self.plan = plan
        self.tags = tags


class FatProfile:
    """Standard class with __dict__ (larger memory footprint)."""

    def __init__(self, user_id: str, email: str, plan: UserPlan, tags: list[str]):
        self.user_id = user_id
        self.email = email
        self.plan = plan
        self.tags = tags


def demo_memory() -> None:
    slim = SlimProfile("u1", "a@example.com", "pro", ["beta"])
    fat = FatProfile("u1", "a@example.com", "pro", ["beta"])
    print("SlimProfile bytes:", sys.getsizeof(slim))
    print("FatProfile bytes :", sys.getsizeof(fat))


def demo_validation() -> None:
    payload = {
        "user_id": "u-100",
        "email": "cto@example.com",
        "plan": "enterprise",
        "company": "Acme Corp",
        "seats": 250,
        "tags": ["vip", "beta"],
    }
    profile = UserProfile.model_validate(payload)
    print("Validated:", profile.model_dump())


if __name__ == "__main__":
    demo_validation()
    demo_memory()

