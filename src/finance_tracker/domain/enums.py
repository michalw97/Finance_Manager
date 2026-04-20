"""Enumerations used across the domain.

Why ``StrEnum`` (Python 3.11+):
    - Values are real strings, so they serialize transparently to JSON.
    - No more magic strings like ``"wpłata"`` scattered across the codebase;
      a typo becomes a static error instead of a silent runtime bug.
"""

from __future__ import annotations

from enum import StrEnum


class TransactionKind(StrEnum):
    """Direction of a cash flow.

    ``INCOME`` increases the balance, ``EXPENSE`` decreases it. These are the
    only two possibilities in our ledger model — every new kind of flow
    (e.g. transfers) would be a new first-class concept, not a new string.
    """

    INCOME = "income"
    EXPENSE = "expense"

    @property
    def sign(self) -> int:
        """Signed multiplier for balance computations."""
        return 1 if self is TransactionKind.INCOME else -1
