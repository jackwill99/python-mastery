from __future__ import annotations

from typing import Protocol

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

# Pro-Tip: Similar to NestJS controllers with DTOs, but FastAPI leverages Python type hints directly for validation/docs and dependency injection.


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=1, max_length=120)
    plan: str = Field(default="free", pattern="^(free|pro)$")


class UserOut(BaseModel):
    user_id: str
    email: EmailStr
    full_name: str
    plan: str


class UserRepo(Protocol):
    async def create(self, payload: UserCreate) -> UserOut: ...

    async def get(self, user_id: str) -> UserOut | None: ...


class InMemoryUserRepo:
    def __init__(self) -> None:
        self._store: dict[str, UserOut] = {}
        self._counter = 0

    async def create(self, payload: UserCreate) -> UserOut:
        self._counter += 1
        user = UserOut(
            user_id=f"u{self._counter}",
            email=payload.email,
            full_name=payload.full_name,
            plan=payload.plan,
        )
        self._store[user.user_id] = user
        return user

    async def get(self, user_id: str) -> UserOut | None:
        return self._store.get(user_id)


repo = InMemoryUserRepo()
app = FastAPI(title="Pythonic User Service", version="1.0.0")


async def get_repo() -> UserRepo:
    return repo


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, repo_dep: UserRepo = Depends(get_repo)) -> UserOut:
    user = await repo_dep.create(payload)
    return user


@app.get("/users/{user_id}", response_model=UserOut)
async def fetch_user(user_id: str, repo_dep: UserRepo = Depends(get_repo)) -> UserOut:
    user = await repo_dep.get(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found")
    return user


# Pythonic backend problem solved: Lean HTTP layer with typed DTOs and DI; you can swap `InMemoryUserRepo` for a real DB without touching handlers.
