"""Фикстуры для упражнений. Логика — в testkit/."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from testkit import load_task

ROOT = Path(__file__).resolve().parent


def use_solutions() -> bool:
    return os.environ.get("COURSES_SOLUTIONS") == "1"


@pytest.fixture
def task(request: pytest.FixtureRequest):
    """Модуль task.py для папки текущего теста (эталон при COURSES_SOLUTIONS=1)."""
    return load_task(Path(request.path).resolve().parent, ROOT, use_solutions())
