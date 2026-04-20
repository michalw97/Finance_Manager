"""End-to-end CLI tests using Typer's CliRunner."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from typer.testing import CliRunner

from finance_tracker.cli.app import app

if TYPE_CHECKING:
    from pathlib import Path


@pytest.fixture
def runner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> CliRunner:
    monkeypatch.setenv("FINANCE_DATA_PATH", str(tmp_path / "transactions.json"))
    monkeypatch.setenv("FINANCE_LOG_LEVEL", "ERROR")
    monkeypatch.setenv("FINANCE_CURRENCY", "EUR")
    return CliRunner()


def test_list_empty_shows_hint(runner: CliRunner) -> None:
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "No transactions" in result.stdout


def test_add_list_balance_cycle(runner: CliRunner) -> None:
    add = runner.invoke(
        app,
        [
            "add",
            "--amount",
            "100.50",
            "--category",
            "salary",
            "--kind",
            "income",
            "--date",
            "2026-01-10",
        ],
    )
    assert add.exit_code == 0, add.stdout
    assert "Added" in add.stdout

    add2 = runner.invoke(
        app,
        [
            "add",
            "--amount",
            "30.25",
            "--category",
            "food",
            "--kind",
            "expense",
            "--date",
            "2026-01-11",
        ],
    )
    assert add2.exit_code == 0, add2.stdout

    listed = runner.invoke(app, ["list"])
    assert listed.exit_code == 0
    assert "salary" in listed.stdout
    assert "food" in listed.stdout

    balance = runner.invoke(app, ["balance"])
    assert balance.exit_code == 0
    assert "70.25" in balance.stdout


def test_list_filter_by_kind(runner: CliRunner) -> None:
    runner.invoke(
        app,
        [
            "add",
            "--amount",
            "1",
            "--category",
            "unique-salary",
            "--kind",
            "income",
            "--date",
            "2026-01-01",
        ],
    )
    runner.invoke(
        app,
        [
            "add",
            "--amount",
            "2",
            "--category",
            "unique-rent",
            "--kind",
            "expense",
            "--date",
            "2026-01-02",
        ],
    )
    only_income = runner.invoke(app, ["list", "--kind", "income"])
    assert only_income.exit_code == 0
    assert "unique-salary" in only_income.stdout
    assert "unique-rent" not in only_income.stdout


def test_delete_unknown_id_exits_nonzero(runner: CliRunner) -> None:
    result = runner.invoke(app, ["delete", "00000000-0000-0000-0000-000000000000"])
    assert result.exit_code == 1
    assert "not found" in result.stdout.lower()


def test_edit_empty_patch_is_rejected(runner: CliRunner) -> None:
    add = runner.invoke(
        app,
        ["add", "--amount", "5", "--category", "a", "--kind", "income", "--date", "2026-01-01"],
    )
    tx_id = add.stdout.split("Added ")[1].split()[0]
    result = runner.invoke(app, ["edit", tx_id])
    assert result.exit_code == 2


def test_menu_add_list_exit_flow(runner: CliRunner) -> None:
    # 1 = add, then supply prompts, then 7 = balance, then 0 = exit
    user_input = "\n".join(
        [
            "1",
            "25.50",
            "freelance",
            "income",
            "2026-01-05",
            "7",
            "0",
            "",
        ]
    )
    result = runner.invoke(app, ["menu"], input=user_input)
    assert result.exit_code == 0, result.stdout
    assert "Added" in result.stdout
    assert "Balance" in result.stdout
    assert "25.50" in result.stdout


def test_edit_partial_update(runner: CliRunner) -> None:
    add = runner.invoke(
        app,
        ["add", "--amount", "5", "--category", "a", "--kind", "income", "--date", "2026-01-01"],
    )
    tx_id = add.stdout.split("Added ")[1].split()[0]
    edited = runner.invoke(app, ["edit", tx_id, "--category", "bonus"])
    assert edited.exit_code == 0
    listed = runner.invoke(app, ["list"])
    assert "bonus" in listed.stdout
