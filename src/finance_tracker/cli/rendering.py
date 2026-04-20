"""Rendering helpers — the only module allowed to touch Rich directly."""

from __future__ import annotations

from typing import TYPE_CHECKING

from rich.console import Console
from rich.table import Table

from finance_tracker.domain.enums import TransactionKind

if TYPE_CHECKING:
    from collections.abc import Iterable

    from finance_tracker.domain.models import Transaction
    from finance_tracker.services.transaction_service import BalanceSummary

console = Console()


def render_transactions(transactions: Iterable[Transaction], *, currency: str) -> None:
    table = Table(
        title="Transactions",
        header_style="bold cyan",
        show_lines=False,
        expand=True,
    )
    table.add_column("ID", style="dim", no_wrap=True, max_width=8)
    table.add_column("Date", no_wrap=True)
    table.add_column("Kind", no_wrap=True)
    table.add_column("Category")
    table.add_column("Amount", justify="right", no_wrap=True)

    any_rows = False
    for tx in transactions:
        any_rows = True
        colour = "green" if tx.kind is TransactionKind.INCOME else "red"
        sign = "+" if tx.kind is TransactionKind.INCOME else "-"
        table.add_row(
            str(tx.id)[:8],
            tx.occurred_on.isoformat(),
            f"[{colour}]{tx.kind.value}[/{colour}]",
            tx.category,
            f"[{colour}]{sign}{tx.amount} {currency}[/{colour}]",
        )
    if not any_rows:
        console.print("[yellow]No transactions yet.[/yellow]")
        return
    console.print(table)


def render_balance(summary: BalanceSummary, *, currency: str) -> None:
    table = Table(title="Balance", header_style="bold cyan", expand=True)
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Total income", f"[green]+{summary.total_income} {currency}[/green]")
    table.add_row("Total expense", f"[red]-{summary.total_expense} {currency}[/red]")
    net_colour = "green" if summary.net >= 0 else "red"
    table.add_row("Net", f"[{net_colour}]{summary.net} {currency}[/{net_colour}]")
    console.print(table)
