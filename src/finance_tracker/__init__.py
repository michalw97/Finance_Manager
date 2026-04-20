"""Finance Tracker — a layered, typed, tested Python application.

The package is intentionally split into four layers:

- ``domain``       — pure, I/O-free business models and rules.
- ``repositories`` — persistence (JSON today, SQL tomorrow).
- ``services``     — use cases orchestrating domain + repository.
- ``cli``          — presentation layer (Typer + Rich).

Outer layers depend on inner layers, never the other way around.
"""

from __future__ import annotations

__version__ = "0.1.0"
