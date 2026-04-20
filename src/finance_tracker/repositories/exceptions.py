"""Typed exceptions for the persistence layer.

Custom exception types are a small but critical habit: they let upper layers
pattern-match on *what* went wrong (``except TransactionNotFoundError``) and
translate that into the right HTTP status code once we switch to FastAPI.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uuid import UUID


class RepositoryError(Exception):
    """Base class for any persistence-layer failure."""


class TransactionNotFoundError(RepositoryError):
    """Raised when a transaction with the given id does not exist."""

    def __init__(self, transaction_id: UUID) -> None:
        self.transaction_id = transaction_id
        super().__init__(f"Transaction {transaction_id} not found")


class RepositoryCorruptedError(RepositoryError):
    """Raised when the underlying storage cannot be parsed into domain models."""
