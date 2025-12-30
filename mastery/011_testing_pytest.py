from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Protocol
from unittest import mock

# Senior Pro-Tip: Similar to Jest + supertest in Node, but pytest fixtures/parametrize and pytest-asyncio give ergonomic async testing with fewer globals.


class PaymentGateway(Protocol):
    async def charge(self, user_id: str, amount_cents: int) -> str: ...


@dataclass
class PaymentService:
    gateway: PaymentGateway

    async def pay(self, user_id: str, amount_cents: int) -> str:
        if amount_cents <= 0:
            raise ValueError("amount must be positive")
        return await self.gateway.charge(user_id, amount_cents)


async def main() -> None:
    # Sanity run
    gateway = mock.AsyncMock(spec=PaymentGateway)
    gateway.charge.return_value = "ok"
    svc = PaymentService(gateway)
    print(await svc.pay("u-1", 1000))


tests = r"""
import asyncio
import pytest
from unittest import mock

from mastery._11_testing_pytest import PaymentService, PaymentGateway


@pytest.fixture(scope="function")
def gateway() -> PaymentGateway:
    gw = mock.AsyncMock(spec=PaymentGateway)
    gw.charge.return_value = "ok"
    return gw


@pytest.fixture(scope="function")
def service(gateway: PaymentGateway) -> PaymentService:
    return PaymentService(gateway=gateway)


@pytest.mark.asyncio
@pytest.mark.parametrize("amount_cents", [1, 100, 10_000])
async def test_pay_success(service: PaymentService, gateway: PaymentGateway, amount_cents: int):
    result = await service.pay("u-1", amount_cents)
    assert result == "ok"
    gateway.charge.assert_awaited_once_with("u-1", amount_cents)


@pytest.mark.asyncio
async def test_pay_rejects_invalid_amount(service: PaymentService):
    with pytest.raises(ValueError):
        await service.pay("u-1", 0)
"""


if __name__ == "__main__":
    asyncio.run(main())

