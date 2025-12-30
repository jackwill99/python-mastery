from __future__ import annotations

import time
from functools import wraps
from typing import Annotated, Callable, Literal, Sequence

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import argon2
from pydantic import BaseModel, Field

# Senior Pro-Tip: OAuth2 + JWT in Python mirrors NestJS passport-jwt or Dart shelf_jwt; Argon2 via passlib gives stronger password hashing than bcrypt defaults.

Role = Literal["admin", "member"]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
JWT_SECRET = "dev-secret"
JWT_ALG = "HS256"


class TokenPayload(BaseModel):
    sub: str
    role: Role
    exp: int


class User(BaseModel):
    user_id: str
    email: str
    password_hash: str
    role: Role = "member"


def create_password_hash(raw: str) -> str:
    return argon2.hash(raw)


def verify_password(raw: str, hashed: str) -> bool:
    return argon2.verify(raw, hashed)


def create_token(user: User, ttl_seconds: int = 3600) -> str:
    payload = TokenPayload(sub=user.user_id, role=user.role, exp=int(time.time()) + ttl_seconds)
    return jwt.encode(payload.model_dump(), JWT_SECRET, algorithm=JWT_ALG)


def decode_token(token: str) -> TokenPayload:
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
        return TokenPayload.model_validate(data)
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token") from exc


def require_roles(roles: Sequence[Role]) -> Callable[[Callable[..., object]], Callable[..., object]]:
    def decorator(fn: Callable[..., object]) -> Callable[..., object]:
        @wraps(fn)
        def wrapper(user: User, *args: object, **kwargs: object) -> object:
            if user.role not in roles:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="forbidden")
            return fn(user, *args, **kwargs)

        return wrapper

    return decorator


async def current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> User:
    payload = decode_token(token)
    # In production, load user from DB; here we mock.
    return User(user_id=payload.sub, email="user@example.com", password_hash="x", role=payload.role)


app = FastAPI(title="Security Service", version="1.0.0")


@app.post("/token")
async def issue_token(email: str, password: str) -> dict[str, str]:
    # Replace with DB lookup + hash verify
    user = User(user_id="u-1", email=email, password_hash=create_password_hash(password), role="admin")
    return {"access_token": create_token(user), "token_type": "bearer"}


@app.get("/admin")
async def admin_area(user: Annotated[User, Depends(current_user)]) -> dict[str, str]:
    secured = require_roles(["admin"])
    secured(lambda u: None)(user)  # role check
    return {"msg": "welcome admin"}


@app.get("/me")
async def me(user: Annotated[User, Depends(current_user)]) -> dict[str, str]:
    return {"user_id": user.user_id, "role": user.role}

