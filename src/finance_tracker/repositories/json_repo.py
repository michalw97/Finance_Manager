"""JSON-file implementation of :class:`TransactionRepository`.

Production-grade details worth noticing:

- **Atomic writes via temp-file + ``os.replace``.** A crash mid-write leaves
  the old file intact instead of corrupting data.
- **Parent directory is created on demand** (``mkdir(parents=True, exist_ok=True)``).
- **All I/O goes through ``pathlib.Path``**, never bare strings.
- **Serialisation uses pydantic's ``model_dump(mode="json")``** so ``Decimal``,
  ``UUID`` and ``datetime`` round-trip without hand-rolled encoders.
"""

from __future__ import annotations

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

from pydantic import TypeAdapter, ValidationError

from finance_tracker.domain.models import Transaction
from finance_tracker.repositories.exceptions import (
    RepositoryCorruptedError,
    TransactionNotFoundError,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from uuid import UUID

_logger = logging.getLogger(__name__)

_TRANSACTION_LIST_ADAPTER: TypeAdapter[list[Transaction]] = TypeAdapter(list[Transaction])


class JsonTransactionRepository:
    """Persist transactions as a JSON array on disk."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._path.parent.mkdir(parents=True, exist_ok=True)

    @property
    def path(self) -> Path:
        return self._path

    # --- read -----------------------------------------------------------------

    def _read(self) -> list[Transaction]:
        if not self._path.exists():
            return []
        raw = self._path.read_text(encoding="utf-8").strip()
        if not raw:
            return []
        try:
            return _TRANSACTION_LIST_ADAPTER.validate_json(raw)
        except ValidationError as exc:
            _logger.exception("Corrupted transaction store at %s", self._path)
            msg = f"Cannot parse {self._path}: {exc.error_count()} validation errors"
            raise RepositoryCorruptedError(msg) from exc
        except json.JSONDecodeError as exc:
            _logger.exception("Invalid JSON in transaction store at %s", self._path)
            msg = f"Invalid JSON at {self._path}: {exc.msg}"
            raise RepositoryCorruptedError(msg) from exc

    def list_all(self) -> list[Transaction]:
        return self._read()

    def get(self, transaction_id: UUID) -> Transaction:
        for tx in self._read():
            if tx.id == transaction_id:
                return tx
        raise TransactionNotFoundError(transaction_id)

    # --- write ----------------------------------------------------------------

    def _write(self, transactions: list[Transaction]) -> None:
        payload = _TRANSACTION_LIST_ADAPTER.dump_json(transactions, indent=2)
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=self._path.parent,
            prefix=f".{self._path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp.write(payload)
            tmp.flush()
            os.fsync(tmp.fileno())
            tmp_path = Path(tmp.name)
        os.replace(tmp_path, self._path)

    def add(self, transaction: Transaction) -> Transaction:
        current = self._read()
        current.append(transaction)
        self._write(current)
        return transaction

    def replace(self, transaction: Transaction) -> Transaction:
        current = self._read()
        for idx, existing in enumerate(current):
            if existing.id == transaction.id:
                current[idx] = transaction
                self._write(current)
                return transaction
        raise TransactionNotFoundError(transaction.id)

    def delete(self, transaction_id: UUID) -> None:
        current = self._read()
        remaining = [tx for tx in current if tx.id != transaction_id]
        if len(remaining) == len(current):
            raise TransactionNotFoundError(transaction_id)
        self._write(remaining)

    def bulk_replace(self, transactions: Iterable[Transaction]) -> None:
        self._write(list(transactions))
