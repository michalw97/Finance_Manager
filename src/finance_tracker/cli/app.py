"""Typer application — composition root for the CLI.

This module is the *composition root*: it is the only place that instantiates
concrete repositories and wires them into services. Every other module takes
collaborators via constructor parameters, which is exactly the pattern you
will reuse with FastAPI's ``Depends(...)``.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Annotated
from uuid import UUID

import typer
from pydantic import ValidationError

from finance_tracker.cli.rendering import console, render_balance, render_transactions
from finance_tracker.config import Settings, configure_logging, get_settings
from finance_tracker.domain.enums import TransactionKind
from finance_tracker.domain.models import NewTransaction, TransactionUpdate
from finance_tracker.repositories.exceptions import (
    RepositoryCorruptedError,
    TransactionNotFoundError,
)
from finance_tracker.repositories.json_repo import JsonTransactionRepository
from finance_tracker.services.transaction_service import (
    EmptyUpdateError,
    TransactionService,
)

app = typer.Typer(
    name="finance",
    help="Finance Tracker — modern Python CLI demo.",
    no_args_is_help=True,
    add_completion=False,
)


def _build_service(settings: Settings) -> TransactionService:
    repo = JsonTransactionRepository(settings.data_path)
    return TransactionService(repo)


@app.callback()
def _bootstrap(ctx: typer.Context) -> None:
    """Configure logging and attach settings + service to the Typer context."""
    settings = get_settings()
    configure_logging(settings.log_level)
    ctx.obj = {"settings": settings, "service": _build_service(settings)}


def _service(ctx: typer.Context) -> TransactionService:
    return ctx.obj["service"]


def _currency(ctx: typer.Context) -> str:
    return ctx.obj["settings"].currency


# --- commands -----------------------------------------------------------------


@app.command("add")
def add_command(
    ctx: typer.Context,
    amount: Annotated[Decimal, typer.Option(prompt=True, help="Amount > 0")],
    category: Annotated[str, typer.Option(prompt=True)],
    kind: Annotated[TransactionKind, typer.Option(prompt=True, case_sensitive=False)],
    occurred_on: Annotated[
        date,
        typer.Option(
            "--date",
            prompt=True,
            formats=["%Y-%m-%d"],
            help="ISO date, e.g. 2026-04-20",
        ),
    ] = date.today(),
) -> None:
    """Create a new transaction."""
    try:
        new_tx = NewTransaction(
            amount=amount, category=category, kind=kind, occurred_on=occurred_on
        )
    except ValidationError as exc:
        console.print(f"[red]Invalid input:[/red] {exc.error_count()} error(s)")
        raise typer.Exit(code=2) from exc
    stored = _service(ctx).create(new_tx)
    console.print(f"[green]Added[/green] {stored.id} ({stored.kind.value} {stored.amount})")


@app.command("list")
def list_command(
    ctx: typer.Context,
    kind: Annotated[
        TransactionKind | None,
        typer.Option("--kind", case_sensitive=False, help="Filter by kind"),
    ] = None,
    category: Annotated[
        str | None, typer.Option("--category", help="Filter by category (exact match)")
    ] = None,
) -> None:
    """List transactions, newest first."""
    render_transactions(
        _service(ctx).list(kind=kind, category=category),
        currency=_currency(ctx),
    )


@app.command("balance")
def balance_command(ctx: typer.Context) -> None:
    """Show aggregated balance."""
    render_balance(_service(ctx).balance(), currency=_currency(ctx))


@app.command("delete")
def delete_command(
    ctx: typer.Context,
    transaction_id: Annotated[UUID, typer.Argument(help="Transaction UUID")],
) -> None:
    """Delete a transaction by id (irreversible)."""
    try:
        _service(ctx).delete(transaction_id)
    except TransactionNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    console.print(f"[yellow]Deleted[/yellow] {transaction_id}")


@app.command("edit")
def edit_command(  # noqa: PLR0913
    ctx: typer.Context,
    transaction_id: Annotated[UUID, typer.Argument()],
    amount: Annotated[Decimal | None, typer.Option(help="New amount")] = None,
    category: Annotated[str | None, typer.Option(help="New category")] = None,
    kind: Annotated[
        TransactionKind | None,
        typer.Option(case_sensitive=False, help="New kind"),
    ] = None,
    occurred_on: Annotated[
        date | None, typer.Option("--date", formats=["%Y-%m-%d"])
    ] = None,
) -> None:
    """Partially update a transaction."""
    try:
        patch = TransactionUpdate(
            amount=amount, category=category, kind=kind, occurred_on=occurred_on
        )
        updated = _service(ctx).update(transaction_id, patch)
    except EmptyUpdateError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=2) from exc
    except TransactionNotFoundError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    except ValidationError as exc:
        console.print(f"[red]Invalid input:[/red] {exc.error_count()} error(s)")
        raise typer.Exit(code=2) from exc
    console.print(f"[green]Updated[/green] {updated.id}")


# --- interactive menu (back-compat with the original main.py UX) --------------


_MENU_TEXT = """\
[bold]Finance Tracker[/bold]
  1. Add transaction
  2. List all
  3. Delete transaction
  4. Edit transaction
  5. List incomes
  6. List expenses
  7. Show balance
  0. Exit\
"""


@app.command("menu")
def menu_command(ctx: typer.Context) -> None:  # noqa: C901, PLR0912
    """Interactive menu (drop-in replacement for the legacy main.py loop)."""
    service = _service(ctx)
    currency = _currency(ctx)

    while True:
        console.print(_MENU_TEXT)
        choice = typer.prompt("Choose", type=int)
        console.print()
        try:
            if choice == 1:
                _prompt_add(service)
            elif choice == 2:
                render_transactions(service.list(), currency=currency)
            elif choice == 3:
                _prompt_delete(service)
            elif choice == 4:
                _prompt_edit(service)
            elif choice == 5:
                render_transactions(
                    service.list(kind=TransactionKind.INCOME), currency=currency
                )
            elif choice == 6:
                render_transactions(
                    service.list(kind=TransactionKind.EXPENSE), currency=currency
                )
            elif choice == 7:
                render_balance(service.balance(), currency=currency)
            elif choice == 0:
                break
            else:
                console.print("[red]Unknown option.[/red]")
        except (ValidationError, EmptyUpdateError, TransactionNotFoundError) as exc:
            console.print(f"[red]{exc}[/red]")
        except RepositoryCorruptedError as exc:
            console.print(f"[red]Data store corrupted:[/red] {exc}")
            raise typer.Exit(code=1) from exc


def _prompt_add(service: TransactionService) -> None:
    try:
        amount = Decimal(typer.prompt("Amount").strip())
    except InvalidOperation as exc:
        console.print("[red]Amount must be a number.[/red]")
        raise typer.Exit(code=2) from exc
    category = typer.prompt("Category").strip()
    kind = TransactionKind(typer.prompt("Kind (income/expense)").strip().lower())
    occurred_on = date.fromisoformat(
        typer.prompt("Date (YYYY-MM-DD)", default=date.today().isoformat()).strip()
    )
    stored = service.create(
        NewTransaction(amount=amount, category=category, kind=kind, occurred_on=occurred_on)
    )
    console.print(f"[green]Added[/green] {stored.id}")


def _prompt_delete(service: TransactionService) -> None:
    transaction_id = UUID(typer.prompt("Transaction ID (UUID)").strip())
    service.delete(transaction_id)
    console.print(f"[yellow]Deleted[/yellow] {transaction_id}")


def _prompt_edit(service: TransactionService) -> None:
    transaction_id = UUID(typer.prompt("Transaction ID (UUID)").strip())
    console.print("Leave blank to skip a field.")
    raw_amount = typer.prompt("New amount", default="").strip()
    raw_category = typer.prompt("New category", default="").strip()
    raw_kind = typer.prompt("New kind (income/expense)", default="").strip()
    raw_date = typer.prompt("New date (YYYY-MM-DD)", default="").strip()
    patch = TransactionUpdate(
        amount=Decimal(raw_amount) if raw_amount else None,
        category=raw_category or None,
        kind=TransactionKind(raw_kind.lower()) if raw_kind else None,
        occurred_on=date.fromisoformat(raw_date) if raw_date else None,
    )
    updated = service.update(transaction_id, patch)
    console.print(f"[green]Updated[/green] {updated.id}")
