from __future__ import annotations

import asyncio
from collections.abc import Iterator
from typing import Any

# Pro-Tip: Pytest fixtures/parametrize feel like Jest group hooks but with powerful fixture graph; async tests run with pytest.mark.asyncio out of the box.


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return a / b


async def async_lookup(value: str) -> str:
    await asyncio.sleep(0.01)
    return value.upper()


# Example tests (save in a tests/ folder). Note: numeric filenames need importlib spec loading.
pytest_example = r"""
import asyncio
import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location("sut", Path(__file__).parent / "011_testing_pytest.py")
module = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)
divide = module.divide
async_lookup = module.async_lookup

@pytest.fixture
def payload() -> dict[str, int]:
    return {"a": 10, "b": 2}

def test_divide_basic(payload):
    assert divide(payload["a"], payload["b"]) == 5

@pytest.mark.parametrize("a,b,expected", [(9, 3, 3), (5, 2.5, 2)])
def test_divide_param(a, b, expected):
    assert divide(a, b) == expected

def test_divide_zero():
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)

@pytest.mark.asyncio
async def test_async_lookup():
    result = await async_lookup("dev")
    assert result == "DEV"
"""

# Pythonic backend problem solved: Concise, composable fixtures and async test support make service contracts testable without heavy mocking frameworks.
