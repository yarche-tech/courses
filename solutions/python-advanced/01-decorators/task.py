"""Эталонные решения задач «Декораторы»."""

from __future__ import annotations

import functools
import inspect
import time
import typing
from collections.abc import Callable


def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)

    wrapper.calls = 0
    return wrapper


def retry(
    times: int,
    exceptions: tuple[type[BaseException], ...] = (Exception,),
    delay: float = 0.0,
    sleep: Callable[[float], None] = time.sleep,
):
    if times < 1:
        raise ValueError(f"times должно быть >= 1, получено {times}")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    sleep(delay)
            raise AssertionError("недостижимо")

        return wrapper

    return decorator


def enforce_types(func):
    hints = typing.get_type_hints(func)
    signature = inspect.signature(func)

    def check(name: str, value: object) -> None:
        expected = hints.get(name)
        if isinstance(expected, type) and not isinstance(value, expected):
            raise TypeError(
                f"{name}: ожидался {expected.__name__}, получен {type(value).__name__}"
            )

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        bound = signature.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            check(name, value)
        result = func(*args, **kwargs)
        check("return", result)
        return result

    return wrapper
