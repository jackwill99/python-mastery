from __future__ import annotations

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, EmailStr, Field, TypeAdapter, field_validator

# Pro-Tip: Dart `@freezed` and NestJS DTOs give immutability/validation; Python adds `__slots__` for memory + Pydantic V2 offers `model_dump` + `TypeAdapter` to validate without class bloat.


class LeanUser:
    """Memory-lean record using slots instead of a dict-backed __dict__."""

    __slots__ = ("user_id", "email", "tags")

    def __init__(self, user_id: str, email: str, tags: list[str]):
        self.user_id = user_id
        self.email = email
        self.tags = tags


Tag = Annotated[str, Field(min_length=1, max_length=32)]


class UserCreate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        frozen=True,
        extra="forbid",
        populate_by_name=True,
    )

    email: EmailStr
    password: Annotated[str, Field(min_length=12, max_length=128)]
    tags: list[Tag] = Field(default_factory=list)
    marketing_opt_in: bool = False

    @field_validator("password")
    @classmethod
    def ensure_password_entropy(cls, value: str) -> str:
        if value.islower() or value.isupper() or value.isdigit():
            raise ValueError("Password must mix cases and digits.")
        return value

    @field_validator("tags")
    @classmethod
    def dedupe_tags(cls, value: list[str]) -> list[str]:
        return sorted(set(value))


class UserOut(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    user_id: str
    email: EmailStr
    created_at: datetime
    tags: list[str]


def to_db_payload(payload: UserCreate) -> dict[str, object]:
    # Keep payload lean; Pydantic models are already validated so we can dump to primitives.
    return {
        "email": payload.email.lower(),
        "password_hash": f"hashed:{payload.password}",  # replace with argon2/bcrypt
        "tags": payload.tags,
        "marketing_opt_in": payload.marketing_opt_in,
    }


def present_user(record: dict[str, object]) -> UserOut:
    # Skip re-validation when you trust the source: model_construct is unsafe but fast.
    return UserOut.model_construct(**record)


def validate_batch(raw_list: list[dict[str, object]]) -> list[UserCreate]:
    adapter = TypeAdapter(list[UserCreate])
    return adapter.validate_python(raw_list)


if __name__ == "__main__":
    incoming = [
        {
            "email": "Senior.Dev@example.com",
            "password": "Sup3rSecurePwd!",
            "tags": ["vip", "vip", "beta"],
        },
        {
            "email": "cto@example.com",
            "password": "A11Weather!",
            "tags": ["admin"],
        },
    ]
    validated = validate_batch(incoming)
    lean = LeanUser("u-123", validated[0].email, validated[0].tags)
    db_payload = to_db_payload(validated[0])
    user = present_user(
        {"user_id": lean.user_id, "email": lean.email, "created_at": datetime.utcnow(), "tags": lean.tags}
    )
    print("Lean instance slots:", lean.__slots__)
    print("DB payload:", db_payload)
    print("API response:", user.model_dump())
