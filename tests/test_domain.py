"""Domain invariants."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from pydantic import ValidationError

from finance_tracker.domain.enums import TransactionKind
from finance_tracker.domain.models import (
    NewTransaction,
    Transaction,
    TransactionUpdate,
)


def test_amount_is_quantised_to_two_decimals() -> None:
    tx = NewTransaction(
        amount=Decimal("10.1"),
        category="x",
        kind=TransactionKind.INCOME,
        occurred_on=date(2026, 1, 1),
    )
    assert tx.amount == Decimal("10.10")


def test_non_positive_amount_is_rejected() -> None:
    with pytest.raises(ValidationError):
        NewTransaction(
            amount=Decimal("0"),
            category="x",
            kind=TransactionKind.INCOME,
            occurred_on=date(2026, 1, 1),
        )


def test_future_date_is_rejected() -> None:
    tomorrow = (datetime.now(tz=UTC) + timedelta(days=1)).date()
    with pytest.raises(ValidationError):
        NewTransaction(
            amount=Decimal("1"),
            category="x",
            kind=TransactionKind.INCOME,
            occurred_on=tomorrow,
        )


def test_category_is_stripped_and_non_empty() -> None:
    tx = NewTransaction(
        amount=Decimal("1"),
        category="  food  ",
        kind=TransactionKind.EXPENSE,
        occurred_on=date(2026, 1, 1),
    )
    assert tx.category == "food"


def test_transaction_is_frozen(sample_income: NewTransaction) -> None:
    tx = Transaction.from_new(sample_income)
    with pytest.raises(ValidationError):
        tx.amount = Decimal("1")


def test_with_update_returns_new_instance(sample_income: NewTransaction) -> None:
    tx = Transaction.from_new(sample_income)
    patched = tx.with_update(TransactionUpdate(category="bonus"))
    assert patched is not tx
    assert patched.category == "bonus"
    assert patched.id == tx.id
    assert tx.category == "salary"


def test_signed_amount_matches_kind(sample_income: NewTransaction) -> None:
    income = Transaction.from_new(sample_income)
    expense = income.with_update(TransactionUpdate(kind=TransactionKind.EXPENSE))
    assert income.signed_amount == income.amount
    assert expense.signed_amount == -expense.amount


def test_transaction_update_is_empty_detects_no_ops() -> None:
    assert TransactionUpdate().is_empty()
    assert not TransactionUpdate(category="x").is_empty()


def test_extra_fields_forbidden() -> None:
    with pytest.raises(ValidationError):
        NewTransaction(
            amount=Decimal("1"),
            category="x",
            kind=TransactionKind.INCOME,
            occurred_on=date(2026, 1, 1),
            notes="nope",  # type: ignore[call-arg]
        )
