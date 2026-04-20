"""Legacy launcher kept for backwards compatibility.

The real entry point is the Typer application exposed at
``finance_tracker.cli:app`` (installed as the ``finance`` console script).
Running ``python main.py`` now boots the interactive ``menu`` command so
existing users still get the familiar numbered menu — just powered by the
new layered architecture.
"""

from __future__ import annotations

from finance_tracker.cli import app


def main() -> None:
    app(["menu"])


if __name__ == "__main__":
    main()
