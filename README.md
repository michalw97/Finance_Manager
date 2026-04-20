# Finance Tracker (2026 edition)

A personal finance CLI used as the **mentoring vehicle** for the
"Python Backend 2026" track. The point is **not** the app itself — it is how the
app is structured. Every layer you see here maps directly to what you will
build in FastAPI later.

## Why this project matters pedagogically

The original `main.py` was a ~200-line monolith: global state, `float` for
money, string-based enums, `len(list)+1` as an ID generator, no tests, no
types. That style was acceptable in ~2015. In 2026, production Python looks
like this repository:

| Concern            | Tool / Pattern                                   |
| ------------------ | ------------------------------------------------ |
| Packaging          | `pyproject.toml` (PEP 621) + `hatchling`         |
| Lint + format      | `ruff` (replaces `black`, `isort`, `flake8`)     |
| Static types       | `mypy --strict`                                  |
| Validation         | `pydantic` v2                                    |
| Settings / env     | `pydantic-settings`                              |
| CLI                | `typer` + `rich`                                 |
| Tests              | `pytest` + `pytest-cov`                          |
| Architecture       | Domain → Repository → Service → CLI (layered)    |
| Money              | `decimal.Decimal` (never `float`)                |
| Identifiers        | `uuid.UUID` (never `len(list)+1`)                |
| Categories / types | `enum.StrEnum`                                   |
| Dates              | `datetime.date` + pydantic validation            |

## Project layout

```text
.
├── pyproject.toml
├── src/
│   └── finance_tracker/
│       ├── __init__.py
│       ├── config.py           # pydantic-settings
│       ├── logging_setup.py    # logging config
│       ├── domain/             # pure, I/O-free business models
│       │   ├── enums.py
│       │   └── models.py
│       ├── repositories/       # persistence (swap JSON ↔ SQL later)
│       │   ├── base.py
│       │   ├── json_repo.py
│       │   └── exceptions.py
│       ├── services/           # business rules / use cases
│       │   └── transaction_service.py
│       └── cli/                # presentation layer (Typer + Rich)
│           ├── app.py
│           └── rendering.py
├── tests/
│   ├── conftest.py
│   ├── test_domain.py
│   ├── test_json_repo.py
│   └── test_service.py
└── main.py                     # thin launcher — `python main.py` still works
```

## Install (for local development)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Usage

```bash
finance add
finance list
finance list --kind income
finance balance
finance delete <id>
finance edit <id>
```

Or launch the interactive menu (same as the legacy `main.py`):

```bash
finance menu
# or
python main.py
```

## Quality gates

```bash
ruff check .
ruff format --check .
mypy
pytest
```
