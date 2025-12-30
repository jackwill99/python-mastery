from __future__ import annotations

import base64
import hashlib
import hmac
import json
import secrets
import time
from typing import TypedDict

# Pro-Tip: Instead of Passport.js or Dart's shelf_jwt, Python stdlib gives you HMAC+PBKDF2; add external libs (pyjwt, passlib, argon2-cffi) in real services.


class TokenPayload(TypedDict):
    sub: str
    exp: int


def pbkdf2_hash(password: str, *, salt: bytes | None = None, rounds: int = 120_000) -> tuple[bytes, bytes]:
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, rounds)
    return salt, digest


def verify_password(password: str, salt: bytes, digest: bytes, rounds: int = 120_000) -> bool:
    new_digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, rounds)
    return hmac.compare_digest(new_digest, digest)


def encode_token(payload: TokenPayload, *, secret: str) -> str:
    body = json.dumps(payload, separators=(",", ":")).encode()
    signature = hmac.new(secret.encode(), body, hashlib.sha256).digest()
    return base64.urlsafe_b64encode(body + b"." + signature).decode()


def decode_token(token: str, *, secret: str) -> TokenPayload:
    raw = base64.urlsafe_b64decode(token.encode())
    body, signature = raw.rsplit(b".", 1)
    expected = hmac.new(secret.encode(), body, hashlib.sha256).digest()
    if not hmac.compare_digest(signature, expected):
        raise ValueError("invalid signature")
    payload: TokenPayload = json.loads(body.decode())
    if payload["exp"] < int(time.time()):
        raise ValueError("token expired")
    return payload


def main() -> None:
    salt, digest = pbkdf2_hash("Sup3rSecret!")
    assert verify_password("Sup3rSecret!", salt, digest)
    token = encode_token({"sub": "u-1", "exp": int(time.time()) + 60}, secret="dev-secret")
    parsed = decode_token(token, secret="dev-secret")
    print("token payload:", parsed)


if __name__ == "__main__":
    main()

# Pythonic backend problem solved: Stateless HMAC tokens and PBKDF2 hashing without extra dependencies; swap in JWT/argon2 for production.
