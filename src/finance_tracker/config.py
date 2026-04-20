"""Application settings.

``pydantic-settings`` turns environment variables and ``.env`` files into a
typed, validated settings object. This is the single source of truth for
runtime configuration — no ``os.environ.get(...)`` scattered through the code.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Runtime configuration, sourced from env vars and ``.env``."""

    model_config = SettingsConfigDict(
        env_prefix="FINANCE_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    data_path: Path = Field(
        default=Path("data/transactions.json"),
        description="Where the JSON repository persists data.",
    )
    log_level: LogLevel = Field(default="INFO", description="Root log level.")
    currency: str = Field(default="PLN", min_length=3, max_length=3)


def get_settings() -> Settings:
    """Factory used as a Typer/FastAPI dependency."""
    return Settings()


def configure_logging(level: LogLevel = "INFO") -> None:
    """Configure root logging once. Idempotent."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
