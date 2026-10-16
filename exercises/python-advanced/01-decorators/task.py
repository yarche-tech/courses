"""Декораторы: три задачи. Условия — README.md рядом и урок на сайте.

Запуск тестов: uv run pytest exercises/python-advanced/01-decorators
"""

from __future__ import annotations

import time
from collections.abc import Callable


def count_calls(func):
    """Задача 1. Считает вызовы в атрибуте `wrapper.calls`, сохраняет метаданные func."""
    raise NotImplementedError


def retry(
    times: int,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    delay: float = 0.0,
    sleep: Callable[[float], None] = time.sleep,
):
    """Задача 2. Декоратор с параметрами: до `times` попыток при исключениях из `exceptions`."""
    raise NotImplementedError


def enforce_types(func):
    """Задача 3. Проверяет аргументы и результат по аннотациям-классам, иначе TypeError."""
    raise NotImplementedError
