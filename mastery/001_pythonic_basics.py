from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# Pro-Tip: In NestJS/Dart you often guard with try/catch + null checks; Python leans on EAFP (do it, handle exceptions) instead of LBYL (pre-check everything).


@dataclass(frozen=True)
class PaymentRequest:
    user_id: str
    amount_cents: int
    currency: str
    token_path: Path


def load_token_eafp(token_path: Path) -> str:
    """EAFP: assume the token file exists and is readable, handle failures explicitly."""
    try:
        return token_path.read_text().strip()
    except FileNotFoundError:
        raise RuntimeError(f"missing token file at {token_path}")
    except OSError as exc:
        raise RuntimeError(f"token file unreadable: {exc}") from exc


def load_token_lbyl(token_path: Path) -> str:
    """LBYL: preflight checks before reading; more verbose and race-prone."""
    if not token_path.exists():
        raise RuntimeError(f"missing token file at {token_path}")
    if not token_path.is_file():
        raise RuntimeError(f"token path is not a file: {token_path}")
    content = token_path.read_text().strip()
    if not content:
        raise RuntimeError("token file is empty")
    return content


def charge_payment(request: PaymentRequest, *, use_eafp: bool = True) -> str:
    loader = load_token_eafp if use_eafp else load_token_lbyl
    token = loader(request.token_path)
    if request.amount_cents <= 0:
        raise ValueError("amount must be positive")
    # Here we'd call a payment gateway SDK; we simulate success.
    return f"charged {request.amount_cents} {request.currency} for {request.user_id} using token {token[:4]}***"


def demo() -> None:
    token_file = Path("payment.token")
    token_file.write_text("tok_live_1234")  # demo only
    req = PaymentRequest(user_id="u-42", amount_cents=2500, currency="USD", token_path=token_file)

    print("EAFP style:", charge_payment(req, use_eafp=True))
    print("LBYL style:", charge_payment(req, use_eafp=False))


if __name__ == "__main__":
    demo()
