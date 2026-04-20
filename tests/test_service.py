"""Service-layer business rules."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from finance_tracker.domain.enums import TransactionKind
from finance_tracker.domain.models import NewTransaction, TransactionUpdate
from finance_tracker.repositories.exceptions import TransactionNotFoundError
from finance_tracker.services.transaction_service import (
    EmptyUpdateError,
    TransactionService,
)


def test_create_and_list(
    service: TransactionService,
    sample_income: NewTransaction,
    sample_expense: NewTransaction,
) -> None:
    service.create(sample_income)
    service.create(sample_expense)
    items = service.list()
    assert len(items) == 2
    assert items[0].occurred_on >= items[1].occurred_on


def test_list_filters_by_kind(
    service: TransactionService,
    sample_income: NewTransaction,
    sample_expense: NewTransaction,
) -> None:
    service.create(sample_income)
    service.create(sample_expense)
    incomes = service.list(kind=TransactionKind.INCOME)
    expenses = service.list(kind=TransactionKind.EXPENSE)
    assert [tx.kind for tx in incomes] == [TransactionKind.INCOME]
    assert [tx.kind for tx in expenses] == [TransactionKind.EXPENSE]


def test_list_filters_by_category_case_insensitive(
    service: TransactionService, sample_income: NewTransaction
) -> None:
    service.create(sample_income)
    assert service.list(category="SALARY") == service.list(category="salary")


def test_balance_sums_with_decimal_precision(service: TransactionService) -> None:
    service.create(
        NewTransaction(
            amount=Decimal("0.10"),
            category="a",
            kind=TransactionKind.INCOME,
            occurred_on=date(2026, 1, 1),
        )
    )
    service.create(
        NewTransaction(
            amount=Decimal("0.20"),
            category="a",
            kind=TransactionKind.INCOME,
            occurred_on=date(2026, 1, 2),
        )
    )
    summary = service.balance()
    assert summary.total_income == Decimal("0.30")
    assert summary.total_expense == Decimal("0")
    assert summary.net == Decimal("0.30")


def test_update_rejects_empty_patch(
    service: TransactionService, sample_income: NewTransaction
) -> None:
    stored = service.create(sample_income)
    with pytest.raises(EmptyUpdateError):
        service.update(stored.id, TransactionUpdate())


def test_update_applies_partial_changes(
    service: TransactionService, sample_income: NewTransaction
) -> None:
    stored = service.create(sample_income)
    updated = service.update(stored.id, TransactionUpdate(amount=Decimal("9999.99")))
    assert updated.amount == Decimal("9999.99")
    assert updated.category == stored.category


def test_delete_removes(service: TransactionService, sample_income: NewTransaction) -> None:
    stored = service.create(sample_income)
    service.delete(stored.id)
    assert service.list() == []
    with pytest.raises(TransactionNotFoundError):
        service.get(stored.id)


def test_update_unknown_id_raises(service: TransactionService) -> None:
    with pytest.raises(TransactionNotFoundError):
        service.update(uuid4(), TransactionUpdate(category="x"))
