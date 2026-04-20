"""Shared pytest fixtures."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from pathlib import Path

from finance_tracker.domain.enums import TransactionKind
from finance_tracker.domain.models import NewTransaction
from finance_tracker.repositories.json_repo import JsonTransactionRepository
from finance_tracker.services.transaction_service import TransactionService


@pytest.fixture
def data_path(tmp_path: Path) -> Path:
    return tmp_path / "transactions.json"


@pytest.fixture
def repo(data_path: Path) -> JsonTransactionRepository:
    return JsonTransactionRepository(data_path)


@pytest.fixture
def service(repo: JsonTransactionRepository) -> TransactionService:
    return TransactionService(repo)


@pytest.fixture
def sample_income() -> NewTransaction:
    return NewTransaction(
        amount=Decimal("1500.50"),
        category="salary",
        kind=TransactionKind.INCOME,
        occurred_on=date(2026, 1, 15),
    )


@pytest.fixture
def sample_expense() -> NewTransaction:
    return NewTransaction(
        amount=Decimal("42.99"),
        category="groceries",
        kind=TransactionKind.EXPENSE,
        occurred_on=date(2026, 1, 16),
    )
