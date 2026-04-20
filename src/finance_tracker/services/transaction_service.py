"""Application services for transactions.

The service layer orchestrates domain models and the repository. It is the
only layer that should contain **business rules** (e.g. "an update must
actually change something", "a balance is income minus expenses"). Routers or
CLI commands just translate user intent into service calls.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING

from finance_tracker.domain.enums import TransactionKind
from finance_tracker.domain.models import Transaction

if TYPE_CHECKING:
    from uuid import UUID

    from finance_tracker.domain.models import NewTransaction, TransactionUpdate
    from finance_tracker.repositories.base import TransactionRepository

_logger = logging.getLogger(__name__)


class EmptyUpdateError(ValueError):
    """Raised when a caller submits a patch with no fields set."""


@dataclass(frozen=True, slots=True)
class BalanceSummary:
    """Aggregated balance figures returned by :meth:`TransactionService.balance`."""

    total_income: Decimal
    total_expense: Decimal

    @property
    def net(self) -> Decimal:
        return self.total_income - self.total_expense


class TransactionService:
    """Use cases exposed to the presentation layer."""

    def __init__(self, repository: TransactionRepository) -> None:
        self._repo = repository

    # --- commands -------------------------------------------------------------

    def create(self, data: NewTransaction) -> Transaction:
        transaction = Transaction.from_new(data)
        stored = self._repo.add(transaction)
        _logger.info("Created transaction %s (%s %s)", stored.id, stored.kind, stored.amount)
        return stored

    def update(self, transaction_id: UUID, patch: TransactionUpdate) -> Transaction:
        if patch.is_empty():
            raise EmptyUpdateError("At least one field must be provided to update")
        existing = self._repo.get(transaction_id)
        updated = existing.with_update(patch)
        stored = self._repo.replace(updated)
        _logger.info("Updated transaction %s", stored.id)
        return stored

    def delete(self, transaction_id: UUID) -> None:
        self._repo.delete(transaction_id)
        _logger.info("Deleted transaction %s", transaction_id)

    # --- queries --------------------------------------------------------------

    def get(self, transaction_id: UUID) -> Transaction:
        return self._repo.get(transaction_id)

    def list(
        self,
        *,
        kind: TransactionKind | None = None,
        category: str | None = None,
    ) -> list[Transaction]:
        """Return transactions sorted newest-first, with optional filters."""
        results = self._repo.list_all()
        if kind is not None:
            results = [tx for tx in results if tx.kind is kind]
        if category is not None:
            needle = category.strip().lower()
            results = [tx for tx in results if tx.category.lower() == needle]
        results.sort(key=lambda tx: (tx.occurred_on, tx.created_at), reverse=True)
        return results

    def balance(self) -> BalanceSummary:
        income = Decimal("0")
        expense = Decimal("0")
        for tx in self._repo.list_all():
            if tx.kind is TransactionKind.INCOME:
                income += tx.amount
            else:
                expense += tx.amount
        return BalanceSummary(total_income=income, total_expense=expense)
