"""Фикстуры для упражнений. Логика — в testkit/."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from testkit import load_task, require_service

ROOT = Path(__file__).resolve().parent
PG_DSN = os.environ.get("COURSES_PG_DSN", "postgresql://courses:courses@localhost:5432/courses")
REDIS_URL = os.environ.get("COURSES_REDIS_URL", "redis://localhost:6379/0")


def use_solutions() -> bool:
    return os.environ.get("COURSES_SOLUTIONS") == "1"


@pytest.fixture
def task(request: pytest.FixtureRequest):
    """Модуль task.py для папки текущего теста (эталон при COURSES_SOLUTIONS=1)."""
    return load_task(Path(request.path).resolve().parent, ROOT, use_solutions())


@pytest.fixture
def pg_dsn() -> str:
    return require_service(PG_DSN, "Postgres")


@pytest.fixture
def redis_url() -> str:
    return require_service(REDIS_URL, "Redis")
