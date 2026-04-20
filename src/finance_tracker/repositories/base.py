"""Repository abstraction.

Why ``typing.Protocol`` instead of ``abc.ABC``:
    - Structural typing ("if it walks like a duck..."): any class exposing
      the right methods satisfies the protocol without explicit inheritance.
    - Keeps the domain free of framework imports.
    - Swapping implementations (JSON → Postgres → in-memory for tests) is a
      one-line change at the composition root.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import Iterable
    from uuid import UUID

    from finance_tracker.domain.models import Transaction


@runtime_checkable
class TransactionRepository(Protocol):
    """Contract that any transaction store must satisfy."""

    def list_all(self) -> list[Transaction]:
        """Return every persisted transaction."""
        ...

    def get(self, transaction_id: UUID) -> Transaction:
        """Return one transaction by id or raise ``TransactionNotFoundError``."""
        ...

    def add(self, transaction: Transaction) -> Transaction:
        """Persist a new transaction and return the stored instance."""
        ...

    def replace(self, transaction: Transaction) -> Transaction:
        """Overwrite an existing transaction (matched by id)."""
        ...

    def delete(self, transaction_id: UUID) -> None:
        """Remove a transaction by id or raise ``TransactionNotFoundError``."""
        ...

    def bulk_replace(self, transactions: Iterable[Transaction]) -> None:
        """Replace the entire store with the given collection (used in tests)."""
        ...
