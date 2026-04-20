"""Domain models for the finance tracker.

Design decisions worth internalising:

1. **Money is ``Decimal``, never ``float``.** ``0.1 + 0.2`` is not ``0.3`` in
   binary floating point; for anything monetary this is malpractice. We store
   amounts as ``Decimal`` with exactly two fractional digits (grosz/cent).

2. **Identifiers are ``UUID``, never ``len(list) + 1``.** Sequential IDs from
   list length are unstable under deletion and impossible to generate in a
   distributed system. ``uuid4`` gives us 122 bits of randomness and zero
   coordination.

3. **Three model shapes for three use cases**
   (a pattern you will reuse verbatim in FastAPI):

   - ``NewTransaction``     — input DTO from the user (no ``id``, no
     ``created_at``).
   - ``TransactionUpdate``  — partial update DTO: every field optional.
   - ``Transaction``        — persisted entity with ``id`` and
     ``created_at``; this is what the repository and service pass around.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_validator

from finance_tracker.domain.enums import TransactionKind  # noqa: TC001

MONEY_FIELD = Annotated[
    Decimal,
    Field(gt=Decimal("0"), max_digits=14, decimal_places=2, description="Amount > 0"),
]
CATEGORY_FIELD = Annotated[
    str,
    Field(min_length=1, max_length=64, description="Human-readable category label"),
]


def _quantize_money(value: Decimal) -> Decimal:
    """Normalise a monetary amount to exactly two fractional digits."""
    return value.quantize(Decimal("0.01"))


class _StrictModel(BaseModel):
    """Shared pydantic configuration for every domain model."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


class NewTransaction(_StrictModel):
    """Input DTO used when a user creates a transaction."""

    amount: MONEY_FIELD
    category: CATEGORY_FIELD
    kind: TransactionKind
    occurred_on: date

    @field_validator("amount", mode="after")
    @classmethod
    def _normalise_amount(cls, value: Decimal) -> Decimal:
        return _quantize_money(value)

    @field_validator("occurred_on", mode="after")
    @classmethod
    def _reject_future_dates(cls, value: date) -> date:
        if value > datetime.now(tz=UTC).date():
            msg = "occurred_on cannot be in the future"
            raise ValueError(msg)
        return value


class TransactionUpdate(_StrictModel):
    """Partial update DTO: any subset of fields may be provided."""

    amount: MONEY_FIELD | None = None
    category: CATEGORY_FIELD | None = None
    kind: TransactionKind | None = None
    occurred_on: date | None = None

    @field_validator("amount", mode="after")
    @classmethod
    def _normalise_amount(cls, value: Decimal | None) -> Decimal | None:
        return None if value is None else _quantize_money(value)

    @field_validator("occurred_on", mode="after")
    @classmethod
    def _reject_future_dates(cls, value: date | None) -> date | None:
        if value is not None and value > datetime.now(tz=UTC).date():
            msg = "occurred_on cannot be in the future"
            raise ValueError(msg)
        return value

    def is_empty(self) -> bool:
        """True when no field was provided — lets the service reject no-ops."""
        return self.model_dump(exclude_none=True) == {}


class Transaction(_StrictModel):
    """Persisted transaction entity."""

    id: UUID = Field(default_factory=uuid4)
    amount: MONEY_FIELD
    category: CATEGORY_FIELD
    kind: TransactionKind
    occurred_on: date
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=UTC))

    @field_validator("amount", mode="after")
    @classmethod
    def _normalise_amount(cls, value: Decimal) -> Decimal:
        return _quantize_money(value)

    @classmethod
    def from_new(cls, data: NewTransaction) -> Transaction:
        """Promote an input DTO to a persisted entity."""
        return cls(
            amount=data.amount,
            category=data.category,
            kind=data.kind,
            occurred_on=data.occurred_on,
        )

    def with_update(self, patch: TransactionUpdate) -> Transaction:
        """Return a new ``Transaction`` with ``patch`` applied.

        Models are frozen, so mutation is forbidden; we copy-on-write. This is
        the same pattern used by SQLAlchemy's ``update()`` and by React state.
        """
        changes = patch.model_dump(exclude_none=True)
        return self.model_copy(update=changes)

    @property
    def signed_amount(self) -> Decimal:
        """Amount with sign applied (positive for income, negative for expense)."""
        return self.amount * self.kind.sign
