"""Инфраструктура тестов упражнений: загрузка заготовки или эталона."""

from __future__ import annotations

import importlib.util
import socket
from pathlib import Path
from types import ModuleType
from urllib.parse import urlparse

import pytest


def task_path(exercise_dir: Path, root: Path, use_solutions: bool) -> Path:
    """Путь к task.py: заготовка из exercises/ или эталон из solutions/."""
    if not use_solutions:
        return exercise_dir / "task.py"
    rel = exercise_dir.relative_to(root / "exercises")
    return root / "solutions" / rel / "task.py"


def load_task(exercise_dir: Path, root: Path, use_solutions: bool) -> ModuleType:
    """Загрузить task.py как модуль с уникальным именем (без sys.modules-коллизий)."""
    path = task_path(exercise_dir, root, use_solutions)
    if not path.is_file():
        raise FileNotFoundError(f"Нет файла {path}")
    parts = path.parent.relative_to(root).parts
    name = "task__" + "__".join(parts).replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def service_available(host: str, port: int, timeout: float = 0.5) -> bool:
    """Открыт ли TCP-порт."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def require_service(url: str, name: str) -> str:
    """Вернуть url, если сервис отвечает, иначе пропустить тест с подсказкой."""
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    if parsed.port is None or not service_available(host, parsed.port):
        pytest.skip(f"{name} недоступен ({host}:{parsed.port}). Запусти: docker compose up -d")
    return url
