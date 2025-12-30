from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, EmailStr, Field

# Pro-Tip: Similar to NestJS controllers with DTOs + filters, but FastAPI uses Python typing directly for validation, dependency injection, and response shaping.

router = APIRouter(prefix="/transactions", tags=["transactions"])


class UserInternal(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    email: EmailStr
    password_hash: str
    balance_cents: int


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: str
    email: EmailStr
    balance_cents: int


class TransactionIn(BaseModel):
    amount_cents: int = Field(gt=0)
    currency: str = Field(pattern="^[A-Z]{3}$")
    recipient: EmailStr


class TransactionOut(BaseModel):
    transaction_id: str
    amount_cents: int
    currency: str
    sender: EmailStr
    recipient: EmailStr
    status: str


class TransactionError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


async def notify_async(transaction_id: str) -> None:
    # Simulate async notification dispatch (e.g., webhook/email)
    return None


async def get_current_user() -> UserInternal:
    # In production, fetch from auth/session; here we simulate.
    return UserInternal(user_id="u-1", email="founder@example.com", password_hash="hashed:secret", balance_cents=50_000)


@router.post(
    "",
    response_model=TransactionOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {"description": "validation error"},
        402: {"description": "insufficient funds"},
    },
)
async def create_transaction(
    payload: TransactionIn,
    bg: BackgroundTasks,
    user: UserInternal = Depends(get_current_user),
) -> TransactionOut:
    if payload.amount_cents > user.balance_cents:
        raise TransactionError("insufficient funds")
    txn_id = "txn_123"  # stub; real service would persist
    bg.add_task(notify_async, txn_id)
    return TransactionOut(
        transaction_id=txn_id,
        amount_cents=payload.amount_cents,
        currency=payload.currency,
        sender=user.email,
        recipient=payload.recipient,
        status="pending",
    )


async def transaction_error_handler(request: Request, exc: TransactionError) -> Response:
    return JSONResponse(
        status_code=status.HTTP_402_PAYMENT_REQUIRED,
        content={"detail": exc.message, "path": request.url.path},
    )


def create_app() -> FastAPI:
    app = FastAPI(title="Financial Service", version="1.0.0")
    app.include_router(router)
    app.add_exception_handler(TransactionError, transaction_error_handler)
    return app


app = create_app()


@router.get("/me", response_model=UserPublic)
async def get_me(user: UserInternal = Depends(get_current_user)) -> UserPublic:
    # Response model strips password_hash automatically, returning only safe fields.
    return user


# Pythonic backend problem solved: Typed request/response models protect sensitive fields, custom exception handler maps domain errors to HTTP, BackgroundTasks handles async side effects without blocking the request.
