"""JSON repository behaviour."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import uuid4

import pytest

from finance_tracker.domain.models import NewTransaction, Transaction
from finance_tracker.repositories.exceptions import (
    RepositoryCorruptedError,
    TransactionNotFoundError,
)
from finance_tracker.repositories.json_repo import JsonTransactionRepository

if TYPE_CHECKING:
    from pathlib import Path


def test_empty_repo_returns_empty_list(repo: JsonTransactionRepository) -> None:
    assert repo.list_all() == []


def test_add_then_list_roundtrip(
    repo: JsonTransactionRepository, sample_income: NewTransaction
) -> None:
    stored = repo.add(Transaction.from_new(sample_income))
    assert repo.list_all() == [stored]


def test_get_missing_raises(repo: JsonTransactionRepository) -> None:
    with pytest.raises(TransactionNotFoundError):
        repo.get(uuid4())


def test_delete_missing_raises(repo: JsonTransactionRepository) -> None:
    with pytest.raises(TransactionNotFoundError):
        repo.delete(uuid4())


def test_replace_missing_raises(
    repo: JsonTransactionRepository, sample_income: NewTransaction
) -> None:
    with pytest.raises(TransactionNotFoundError):
        repo.replace(Transaction.from_new(sample_income))


def test_persistence_survives_new_instance(data_path: Path, sample_income: NewTransaction) -> None:
    repo_a = JsonTransactionRepository(data_path)
    stored = repo_a.add(Transaction.from_new(sample_income))
    repo_b = JsonTransactionRepository(data_path)
    assert repo_b.list_all() == [stored]


def test_corrupted_file_raises(data_path: Path) -> None:
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text("{not json", encoding="utf-8")
    repo = JsonTransactionRepository(data_path)
    with pytest.raises(RepositoryCorruptedError):
        repo.list_all()


def test_blank_file_is_treated_as_empty(data_path: Path) -> None:
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text("   \n", encoding="utf-8")
    repo = JsonTransactionRepository(data_path)
    assert repo.list_all() == []
