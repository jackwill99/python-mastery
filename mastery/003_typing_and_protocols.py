from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

# Pro-Tip: Dart abstract classes define shape; Python's Protocols are structural (duck-typed) and can be runtime-checked. Metaclasses here act like compile-time linters for plugin docs—similar to NestJS provider decorators, but enforced at import.


class DocEnforcingMeta(type):
    """Metaclass that enforces documentation standards and registers payment gateway plugins."""

    registry: dict[str, type["PaymentGateway"]] = {}
    required_doc_phrase = "Payment Gateway Plugin"

    def __new__(mcls, name: str, bases: tuple[type, ...], ns: dict[str, object]):
        cls = super().__new__(mcls, name, bases, ns)
        plugin_name = getattr(cls, "plugin_name", None)
        doc = (cls.__doc__ or "").strip()
        if plugin_name:
            if plugin_name in mcls.registry:
                raise ValueError(f"Duplicate plugin_name '{plugin_name}' for {name}")
            if mcls.required_doc_phrase not in doc:
                raise ValueError(f"{name} missing required doc phrase: '{mcls.required_doc_phrase}'")
            mcls.registry[plugin_name] = cls
        return cls


@runtime_checkable
class PaymentGateway(Protocol):
    plugin_name: str

    def charge(self, amount_cents: int, currency: str, token: str) -> str: ...

    def refund(self, charge_id: str, amount_cents: int | None = None) -> str: ...


@dataclass
class StripePlugin(metaclass=DocEnforcingMeta):
    """Payment Gateway Plugin: Stripe implementation."""

    plugin_name: str = "stripe"

    def charge(self, amount_cents: int, currency: str, token: str) -> str:
        if amount_cents <= 0:
            raise ValueError("amount must be positive")
        return f"stripe_charge_{amount_cents}_{currency}_{token[:4]}"

    def refund(self, charge_id: str, amount_cents: int | None = None) -> str:
        return f"stripe_refund_{charge_id}_{amount_cents or 'full'}"


@dataclass
class AdyenPlugin(metaclass=DocEnforcingMeta):
    """Payment Gateway Plugin: Adyen implementation."""

    plugin_name: str = "adyen"

    def charge(self, amount_cents: int, currency: str, token: str) -> str:
        if currency not in {"USD", "EUR"}:
            raise ValueError("unsupported currency")
        return f"adyen_charge_{amount_cents}_{currency}_{token[:4]}"

    def refund(self, charge_id: str, amount_cents: int | None = None) -> str:
        return f"adyen_refund_{charge_id}_{amount_cents or 'full'}"


def process_payment(gateway_name: str, amount_cents: int, currency: str, token: str) -> str:
    cls = DocEnforcingMeta.registry[gateway_name]
    gateway: PaymentGateway = cls()
    return gateway.charge(amount_cents, currency, token)


def process_refund(gateway_name: str, charge_id: str, amount_cents: int | None = None) -> str:
    cls = DocEnforcingMeta.registry[gateway_name]
    gateway: PaymentGateway = cls()
    return gateway.refund(charge_id, amount_cents)


def list_gateways() -> list[str]:
    return sorted(DocEnforcingMeta.registry.keys())


if __name__ == "__main__":
    print("Registered gateways:", list_gateways())
    charge_id = process_payment("stripe", 2000, "USD", "tok_abc123")
    print("Charge:", charge_id)
    print("Refund:", process_refund("stripe", charge_id))
