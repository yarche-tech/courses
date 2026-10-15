# Сайт курсов — MVP: план реализации

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Каркас сайта курсов на MkDocs Material с 8 разделами, инфраструктура локальных задач (заготовка/тесты/эталон) и первая полная тема «Декораторы», опубликованные на GitHub Pages.

**Architecture:** Статический сайт (`docs/` → MkDocs Material → GitHub Pages через Actions). Задачи лежат вне сайта: `exercises/<раздел>/<NN-тема>/` (заготовка + тесты) и `solutions/…` (эталон). Фикстура `task` в корневом `conftest.py` загружает заготовку или эталон (`COURSES_SOLUTIONS=1`) по пути, с уникальным именем модуля. Мета-тесты в `tests/` гарантируют: эталон проходит, заготовка падает, структура и front matter корректны.

**Tech Stack:** Python ≥ 3.13 (через uv), pytest, PyYAML, mkdocs-material, Docker Compose (Postgres 17, Redis 7), GitHub Actions, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-10-15-courses-site-design.md`

## Global Constraints

- Python `>=3.13`; зависимости через `uv` (`uv sync`, `uv run …`).
- 8 разделов, slug'и ровно: `python-advanced`, `cs-fundamentals`, `backend`, `architecture`, `ml`, `cv`, `llm`, `applied-ai`.
- Задача: `exercises/<slug>/NN-<topic>/{task.py,test_task.py,README.md}`, эталон: `solutions/<slug>/NN-<topic>/task.py`.
- Тесты упражнений обращаются к коду только через фикстуру `task` (никаких `import task`).
- Урок: `docs/<slug>/NN-<topic>.md` с front matter `title`, `status: draft|reviewed`, `sources: [..]`.
- `docs/superpowers/` не публикуется (`exclude_docs`).
- Сайт и репозиторий публичные: `https://github.com/yarche-tech/courses`, `https://yarche-tech.github.io/courses/`.
- Контент из репозиториев без лицензии не копируется дословно; MIT-источники указываются в `sources` и `docs/credits.md`.
- Решения пользователя не коммитятся в `main` (локальная ветка `work`).
- Тексты сайта, сообщения об ошибках и комментарии — на русском.
- `mkdocs build --strict` должен проходить.

## Review Focus

1. **Одинаковые имена файлов в разных упражнениях** (`task.py`, `test_task.py` в каждой теме): ожидается, что тесты разных тем не путают модули и не падают с «import file mismatch» → Task 2 (уникальные имена модулей) и Task 2 (проверка `--import-mode=importlib` в pyproject).
2. **Запуск pytest из папки упражнения**, а не из корня: ожидается тот же результат → Task 4 (`test_solution_passes_from_exercise_dir`).
3. **Postgres/Redis не запущены или порт занят другим проектом**: ожидается skip с подсказкой `docker compose up -d` и возможность сменить порт/DSN через переменные окружения → Task 3.
4. **Заготовка случайно содержит решение** (тесты на ней проходят): ожидается падение CI → Task 4 (`test_stub_fails`).
5. **Урок без/с битым front matter** или неизвестным `status`: ожидается падение тестов, а не тихая публикация → Task 5 (`test_lesson_front_matter`).

---

## Файловая структура

```
pyproject.toml            зависимости, конфиг pytest
.python-version           3.13
.gitignore
README.md                 как пользоваться
CLAUDE.md                 правила добавления тем для будущих сессий
PROGRESS.md               чек-лист тем
conftest.py               фикстуры task, pg_dsn, redis_url (тонкие, логика в testkit)
testkit/__init__.py       task_path, load_task, service_available, require_service
docker-compose.yml        Postgres 17 + Redis 7 (порты настраиваются)
tests/test_testkit.py     юнит-тесты testkit + конфиг pytest
tests/test_structure.py   структура упражнений, разделов, front matter
tests/test_exercises.py   эталон проходит / заготовка падает
exercises/python-advanced/01-decorators/{task.py,test_task.py,README.md}
solutions/python-advanced/01-decorators/task.py
mkdocs.yml
docs/index.md, docs/credits.md, docs/javascripts/mathjax.js
docs/<slug>/index.md ×8
docs/python-advanced/01-decorators.md
.github/workflows/site.yml, .github/workflows/tests.yml
```

---

### Task 1: Python-проект и uv

**Files:**
- Create: `pyproject.toml`, `.python-version`, `.gitignore`

**Interfaces:**
- Produces: окружение `uv run pytest`, `uv run mkdocs`; pytest-конфиг `testpaths=["tests"]`, `pythonpath=["."]`, `--import-mode=importlib`.

- [ ] **Step 1: Создать `pyproject.toml`**

```toml
[project]
name = "courses"
version = "0.1.0"
description = "Личные курсы: 8 направлений, уроки + задачи с тестами"
requires-python = ">=3.13"
dependencies = []

[dependency-groups]
dev = ["pytest>=8.3", "pyyaml>=6.0"]
docs = ["mkdocs-material>=9.6"]

[tool.uv]
package = false
default-groups = ["dev", "docs"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
addopts = "--import-mode=importlib"
```

- [ ] **Step 2: Создать `.python-version`** с одной строкой `3.13`.

- [ ] **Step 3: Создать `.gitignore`**

```
.venv/
__pycache__/
.pytest_cache/
site/
```

- [ ] **Step 4: Установить окружение**

Run: `uv sync`
Expected: создан `.venv`, установлен Python 3.13, pytest, pyyaml, mkdocs-material; появился `uv.lock`.

- [ ] **Step 5: Проверить**

Run: `uv run python --version && uv run pytest`
Expected: `Python 3.13.x`; pytest завершается с кодом 5 («no tests ran») — тестов ещё нет, это норма.

- [ ] **Step 6: Commit**

```bash
git add pyproject.toml .python-version .gitignore uv.lock
git commit -m "chore: python-проект на uv"
```

---

### Task 2: testkit — загрузка заготовки/эталона

**Files:**
- Create: `testkit/__init__.py`, `conftest.py`
- Test: `tests/test_testkit.py`

**Interfaces:**
- Consumes: pytest-конфиг из Task 1.
- Produces:
  - `testkit.task_path(exercise_dir: Path, root: Path, use_solutions: bool) -> Path`
  - `testkit.load_task(exercise_dir: Path, root: Path, use_solutions: bool) -> ModuleType`
  - фикстура `task` (корневой `conftest.py`) → модуль заготовки или эталона для папки текущего теста.

- [ ] **Step 1: Написать падающие тесты** — `tests/test_testkit.py`

```python
import tomllib
from pathlib import Path

import pytest

from testkit import load_task, task_path

ROOT = Path(__file__).resolve().parents[1]


def make_exercise(root: Path, rel: str, body: str, solution: str | None = None) -> Path:
    exercise = root / "exercises" / rel
    exercise.mkdir(parents=True)
    (exercise / "task.py").write_text(body, encoding="utf-8")
    if solution is not None:
        sol = root / "solutions" / rel
        sol.mkdir(parents=True)
        (sol / "task.py").write_text(solution, encoding="utf-8")
    return exercise


def test_task_path_stub(tmp_path):
    exercise = make_exercise(tmp_path, "python-advanced/01-x", "")
    assert task_path(exercise, tmp_path, use_solutions=False) == exercise / "task.py"


def test_task_path_solution(tmp_path):
    exercise = make_exercise(tmp_path, "python-advanced/01-x", "", solution="")
    expected = tmp_path / "solutions" / "python-advanced" / "01-x" / "task.py"
    assert task_path(exercise, tmp_path, use_solutions=True) == expected


def test_load_task_picks_stub_or_solution(tmp_path):
    exercise = make_exercise(tmp_path, "a/01-x", "VALUE = 'stub'", solution="VALUE = 'solution'")
    assert load_task(exercise, tmp_path, use_solutions=False).VALUE == "stub"
    assert load_task(exercise, tmp_path, use_solutions=True).VALUE == "solution"


def test_same_file_names_give_distinct_modules(tmp_path):
    first = make_exercise(tmp_path, "a/01-x", "VALUE = 1")
    second = make_exercise(tmp_path, "b/01-x", "VALUE = 2")
    m1 = load_task(first, tmp_path, use_solutions=False)
    m2 = load_task(second, tmp_path, use_solutions=False)
    assert (m1.VALUE, m2.VALUE) == (1, 2)
    assert m1.__name__ != m2.__name__


def test_missing_solution_names_the_path(tmp_path):
    exercise = make_exercise(tmp_path, "a/01-x", "")
    with pytest.raises(FileNotFoundError, match="solutions"):
        load_task(exercise, tmp_path, use_solutions=True)


def test_pytest_uses_importlib_mode():
    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert "--import-mode=importlib" in config["tool"]["pytest"]["ini_options"]["addopts"]
```

- [ ] **Step 2: Убедиться, что падают**

Run: `uv run pytest tests/test_testkit.py -v`
Expected: ошибка `ModuleNotFoundError: No module named 'testkit'`.

- [ ] **Step 3: Реализовать** — `testkit/__init__.py`

```python
"""Инфраструктура тестов упражнений: загрузка заготовки или эталона."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


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
```

- [ ] **Step 4: Корневой `conftest.py`**

```python
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
```

- [ ] **Step 5: Тесты проходят**

Run: `uv run pytest tests/test_testkit.py -v`
Expected: 6 passed.

- [ ] **Step 6: Commit**

```bash
git add testkit conftest.py tests/test_testkit.py
git commit -m "feat: testkit — загрузка заготовки или эталона"
```

---

### Task 3: Postgres/Redis для задач

**Files:**
- Create: `docker-compose.yml`
- Modify: `testkit/__init__.py` (добавить `service_available`, `require_service`), `conftest.py` (фикстуры `pg_dsn`, `redis_url`)
- Test: `tests/test_testkit.py` (дописать)

**Interfaces:**
- Produces:
  - `testkit.service_available(host: str, port: int, timeout: float = 0.5) -> bool`
  - `testkit.require_service(url: str, name: str) -> str` — возвращает url или вызывает `pytest.skip` с подсказкой `docker compose up -d`.
  - фикстуры `pg_dsn` (env `COURSES_PG_DSN`, по умолчанию `postgresql://courses:courses@localhost:5432/courses`) и `redis_url` (env `COURSES_REDIS_URL`, по умолчанию `redis://localhost:6379/0`).

- [ ] **Step 1: Дописать падающие тесты** в `tests/test_testkit.py`

```python
import socket

from testkit import require_service, service_available


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_service_available_true_for_listening_port():
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        assert service_available("127.0.0.1", server.getsockname()[1])


def test_service_available_false_for_closed_port():
    assert not service_available("127.0.0.1", free_port())


def test_require_service_skips_with_hint():
    url = f"postgresql://u:p@127.0.0.1:{free_port()}/db"
    with pytest.raises(pytest.skip.Exception, match="docker compose up -d"):
        require_service(url, "Postgres")


def test_require_service_returns_url_when_up():
    with socket.socket() as server:
        server.bind(("127.0.0.1", 0))
        server.listen()
        url = f"redis://127.0.0.1:{server.getsockname()[1]}/0"
        assert require_service(url, "Redis") == url
```

- [ ] **Step 2: Убедиться, что падают**

Run: `uv run pytest tests/test_testkit.py -v`
Expected: `ImportError: cannot import name 'require_service'`.

- [ ] **Step 3: Реализовать** — дописать в `testkit/__init__.py`

```python
import socket
from urllib.parse import urlparse

import pytest


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
```

(Импорты `socket`, `urlparse`, `pytest` — в общий блок импортов наверху файла.)

- [ ] **Step 4: Фикстуры** — дописать в `conftest.py`

```python
from testkit import require_service

PG_DSN = os.environ.get("COURSES_PG_DSN", "postgresql://courses:courses@localhost:5432/courses")
REDIS_URL = os.environ.get("COURSES_REDIS_URL", "redis://localhost:6379/0")


@pytest.fixture
def pg_dsn() -> str:
    return require_service(PG_DSN, "Postgres")


@pytest.fixture
def redis_url() -> str:
    return require_service(REDIS_URL, "Redis")
```

- [ ] **Step 5: `docker-compose.yml`** (порт меняется, если 5432/6379 заняты другим проектом)

```yaml
services:
  postgres:
    image: postgres:17
    environment:
      POSTGRES_USER: courses
      POSTGRES_PASSWORD: courses
      POSTGRES_DB: courses
    ports:
      - "127.0.0.1:${COURSES_PG_PORT:-5432}:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
  redis:
    image: redis:7
    ports:
      - "127.0.0.1:${COURSES_REDIS_PORT:-6379}:6379"

volumes:
  pgdata: {}
```

- [ ] **Step 6: Проверить**

Run: `uv run pytest tests/test_testkit.py -v && docker compose config -q && echo compose-ok`
Expected: 10 passed; `compose-ok`.

- [ ] **Step 7: Commit**

```bash
git add testkit conftest.py tests/test_testkit.py docker-compose.yml
git commit -m "feat: Postgres/Redis для задач, skip с подсказкой при недоступности"
```

---

### Task 4: Задачи «Декораторы» + мета-тесты упражнений

**Files:**
- Create: `exercises/python-advanced/01-decorators/{task.py,test_task.py,README.md}`, `solutions/python-advanced/01-decorators/task.py`
- Test: `tests/test_exercises.py`, `tests/test_structure.py`

**Interfaces:**
- Consumes: фикстура `task` (Task 2).
- Produces: в `task.py` функции `count_calls(func)`, `retry(times, exceptions=(Exception,), delay=0.0, sleep=time.sleep)`, `enforce_types(func)`; `tests/test_structure.py::ROOT`, `SECTIONS` (дополняется в Task 5).

- [ ] **Step 1: Мета-тесты** — `tests/test_exercises.py`

```python
"""Эталон проходит тесты, заготовка — нет. Ловит «решение в заготовке» и сломанные тесты."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXERCISES = sorted(p.parent for p in (ROOT / "exercises").glob("*/*/test_task.py"))
IDS = [str(p.relative_to(ROOT / "exercises")) for p in EXERCISES]


def run_pytest(target: Path, solutions: bool, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "COURSES_SOLUTIONS": "1" if solutions else "0"}
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(target)],
        cwd=cwd, env=env, capture_output=True, text=True,
    )


def test_there_are_exercises():
    assert EXERCISES, "нет ни одного упражнения"


@pytest.mark.parametrize("exercise_dir", EXERCISES, ids=IDS)
def test_solution_passes(exercise_dir):
    result = run_pytest(exercise_dir, solutions=True)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("exercise_dir", EXERCISES, ids=IDS)
def test_stub_fails(exercise_dir):
    result = run_pytest(exercise_dir, solutions=False)
    assert result.returncode == 1, result.stdout + result.stderr


def test_solution_passes_from_exercise_dir():
    exercise_dir = EXERCISES[0]
    result = run_pytest(Path("."), solutions=True, cwd=exercise_dir)
    assert result.returncode == 0, result.stdout + result.stderr
```

- [ ] **Step 2: Структурные тесты** — `tests/test_structure.py`

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def topic_dirs(base: str) -> list[Path]:
    return sorted(p for p in (ROOT / base).glob("*/*") if p.is_dir() and p.name != "__pycache__")


def test_every_exercise_is_complete():
    for d in topic_dirs("exercises"):
        for name in ("task.py", "test_task.py", "README.md"):
            assert (d / name).is_file(), f"нет {d / name}"
        solution = ROOT / "solutions" / d.relative_to(ROOT / "exercises") / "task.py"
        assert solution.is_file(), f"нет эталона {solution}"


def test_every_solution_has_exercise():
    for d in topic_dirs("solutions"):
        exercise = ROOT / "exercises" / d.relative_to(ROOT / "solutions")
        assert exercise.is_dir(), f"эталон без упражнения: {d}"
```

- [ ] **Step 3: Убедиться, что падают**

Run: `uv run pytest tests/test_exercises.py -v`
Expected: `test_there_are_exercises` FAILED («нет ни одного упражнения»), `test_solution_passes_from_exercise_dir` — IndexError.

- [ ] **Step 4: Тесты упражнения** — `exercises/python-advanced/01-decorators/test_task.py`

```python
import pytest


# --- Задача 1: count_calls ---------------------------------------------------

def test_count_calls_counts(task):
    @task.count_calls
    def add(a, b):
        return a + b

    assert add.calls == 0
    assert add(1, 2) == 3
    add(3, 4)
    assert add.calls == 2


def test_count_calls_independent_counters(task):
    @task.count_calls
    def f():
        pass

    @task.count_calls
    def g():
        pass

    f(); f(); g()
    assert (f.calls, g.calls) == (2, 1)


def test_count_calls_keeps_metadata(task):
    @task.count_calls
    def documented(x: int) -> int:
        """Док."""
        return x

    assert documented.__name__ == "documented"
    assert documented.__doc__ == "Док."
    assert documented.__wrapped__(5) == 5


def test_count_calls_counts_failed_calls(task):
    @task.count_calls
    def boom():
        raise ValueError

    with pytest.raises(ValueError):
        boom()
    assert boom.calls == 1


# --- Задача 2: retry ---------------------------------------------------------

def make_flaky(fail_times: int, exc: type[Exception] = ConnectionError):
    state = {"calls": 0}

    def flaky():
        state["calls"] += 1
        if state["calls"] <= fail_times:
            raise exc("fail")
        return "ok"

    return flaky, state


def test_retry_succeeds_after_failures(task):
    sleeps: list[float] = []
    flaky, state = make_flaky(2)
    wrapped = task.retry(3, delay=0.5, sleep=sleeps.append)(flaky)
    assert wrapped() == "ok"
    assert state["calls"] == 3
    assert sleeps == [0.5, 0.5]


def test_retry_reraises_last_after_exhausting(task):
    sleeps: list[float] = []
    flaky, state = make_flaky(10)
    wrapped = task.retry(3, sleep=sleeps.append)(flaky)
    with pytest.raises(ConnectionError):
        wrapped()
    assert state["calls"] == 3
    assert len(sleeps) == 2  # после последней попытки не спим


def test_retry_does_not_catch_other_exceptions(task):
    flaky, state = make_flaky(1, exc=KeyError)
    wrapped = task.retry(3, exceptions=(ConnectionError,), sleep=lambda s: None)(flaky)
    with pytest.raises(KeyError):
        wrapped()
    assert state["calls"] == 1


def test_retry_passes_arguments_and_keeps_name(task):
    @task.retry(2, sleep=lambda s: None)
    def mul(a, *, b):
        return a * b

    assert mul(3, b=4) == 12
    assert mul.__name__ == "mul"


@pytest.mark.parametrize("times", [0, -1])
def test_retry_rejects_non_positive_times(task, times):
    with pytest.raises(ValueError):
        task.retry(times)


# --- Задача 3: enforce_types -------------------------------------------------

def test_enforce_types_accepts_valid(task):
    @task.enforce_types
    def greet(name: str, times: int = 1) -> str:
        return name * times

    assert greet("a", 3) == "aaa"
    assert greet(name="b") == "b"


def test_enforce_types_rejects_bad_argument(task):
    @task.enforce_types
    def greet(name: str, times: int = 1) -> str:
        return name * times

    with pytest.raises(TypeError, match="times"):
        greet("a", "3")


def test_enforce_types_checks_return(task):
    @task.enforce_types
    def broken() -> int:
        return "not int"

    with pytest.raises(TypeError, match="return"):
        broken()


def test_enforce_types_ignores_unannotated_and_generics(task):
    @task.enforce_types
    def f(a, items: list[int]) -> None:
        return None

    assert f(object(), ["x"]) is None


def test_enforce_types_keeps_name(task):
    @task.enforce_types
    def named(x: int) -> int:
        return x

    assert named.__name__ == "named"
```

- [ ] **Step 5: Заготовка** — `exercises/python-advanced/01-decorators/task.py`

```python
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
```

- [ ] **Step 6: Условие** — `exercises/python-advanced/01-decorators/README.md`

```markdown
# Декораторы — задачи

Урок: https://yarche-tech.github.io/courses/python-advanced/01-decorators/

Запуск: `uv run pytest exercises/python-advanced/01-decorators`

## 1. `count_calls(func)`
Декоратор считает вызовы обёрнутой функции в атрибуте `calls` (начинается с 0).
Неудачные вызовы (с исключением) тоже считаются. У каждой функции свой счётчик.
`__name__`, `__doc__`, `__wrapped__` должны сохраниться.

## 2. `retry(times, exceptions=(Exception,), delay=0.0, sleep=time.sleep)`
Декоратор с параметрами. Вызывает функцию до `times` раз, пока она бросает
исключение из `exceptions`; между попытками вызывает `sleep(delay)` (после последней — нет).
Если попытки кончились — пробрасывает последнее исключение. Прочие исключения
пробрасываются сразу. `times < 1` → `ValueError` при вызове `retry(...)`.

## 3. `enforce_types(func)`
При каждом вызове проверяет аргументы (включая значения по умолчанию) и результат
по аннотациям. Проверяются только аннотации-классы (`int`, `str`, свои классы, `None`);
обобщённые (`list[int]`) и отсутствующие — игнорируются. Нарушение → `TypeError`,
в сообщении имя параметра или `return`.
```

- [ ] **Step 7: Эталон** — `solutions/python-advanced/01-decorators/task.py`

```python
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
```

- [ ] **Step 8: Проверить эталон и заготовку напрямую**

Run: `COURSES_SOLUTIONS=1 uv run pytest exercises/python-advanced/01-decorators -q`
Expected: 15 passed.

Run: `uv run pytest exercises/python-advanced/01-decorators -q`
Expected: 15 failed (NotImplementedError), код возврата 1.

- [ ] **Step 9: Мета-тесты проходят**

Run: `uv run pytest -v`
Expected: все тесты `tests/` passed (testkit 10, exercises 4, structure 2).

- [ ] **Step 10: Commit**

```bash
git add exercises solutions tests/test_exercises.py tests/test_structure.py
git commit -m "feat: задачи «Декораторы» и мета-тесты упражнений"
```

---

### Task 5: Сайт MkDocs — каркас и 8 разделов

**Files:**
- Create: `mkdocs.yml`, `docs/index.md`, `docs/credits.md`, `docs/javascripts/mathjax.js`, `docs/<slug>/index.md` ×8
- Modify: `tests/test_structure.py` (разделы и front matter)

**Interfaces:**
- Consumes: `tests/test_structure.py::ROOT`.
- Produces: `SECTIONS` в `tests/test_structure.py`; `nav` в `mkdocs.yml`, куда Task 6 добавляет урок.

- [ ] **Step 1: Дописать падающие тесты** в `tests/test_structure.py`

```python
import re

import pytest
import yaml

SECTIONS = [
    "python-advanced", "cs-fundamentals", "backend", "architecture",
    "ml", "cv", "llm", "applied-ai",
]
LESSONS = sorted((ROOT / "docs").glob("*/[0-9][0-9]-*.md"))


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert match, f"{path}: нет front matter"
    return yaml.safe_load(match.group(1)) or {}


def test_every_section_has_index():
    for slug in SECTIONS:
        assert (ROOT / "docs" / slug / "index.md").is_file(), f"нет docs/{slug}/index.md"


@pytest.mark.parametrize("lesson", LESSONS, ids=[p.stem for p in LESSONS])
def test_lesson_front_matter(lesson):
    meta = front_matter(lesson)
    assert meta.get("title"), f"{lesson}: нет title"
    assert meta.get("status") in {"draft", "reviewed"}, f"{lesson}: status draft|reviewed"
    assert isinstance(meta.get("sources"), list) and meta["sources"], f"{lesson}: нет sources"


def test_front_matter_rejects_missing_block(tmp_path):
    bad = tmp_path / "01-bad.md"
    bad.write_text("# без front matter\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="нет front matter"):
        front_matter(bad)
```

- [ ] **Step 2: Убедиться, что падают**

Run: `uv run pytest tests/test_structure.py -v`
Expected: `test_every_section_has_index` FAILED («нет docs/python-advanced/index.md»).

- [ ] **Step 3: `mkdocs.yml`**

```yaml
site_name: Курсы
site_description: 8 направлений — от Python Advanced до Applied AI
site_url: https://yarche-tech.github.io/courses/
repo_url: https://github.com/yarche-tech/courses
repo_name: yarche-tech/courses
edit_uri: edit/main/docs/

exclude_docs: |
  superpowers/

theme:
  name: material
  language: ru
  features:
    - navigation.tabs
    - navigation.sections
    - navigation.indexes
    - navigation.footer
    - navigation.top
    - search.highlight
    - search.suggest
    - content.code.copy
    - content.action.edit
  palette:
    - media: "(prefers-color-scheme: light)"
      scheme: default
      toggle:
        icon: material/brightness-7
        name: Тёмная тема
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      toggle:
        icon: material/brightness-4
        name: Светлая тема

plugins:
  - search:
      lang: [ru, en]

markdown_extensions:
  - admonition
  - attr_list
  - md_in_html
  - toc:
      permalink: true
  - pymdownx.details
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.inlinehilite
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.arithmatex:
      generic: true
  - pymdownx.tasklist:
      custom_checkbox: true

extra_javascript:
  - javascripts/mathjax.js
  - https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js

nav:
  - Главная: index.md
  - Python Advanced:
      - python-advanced/index.md
  - CS Fundamentals:
      - cs-fundamentals/index.md
  - Backend:
      - backend/index.md
  - Architecture:
      - architecture/index.md
  - ML:
      - ml/index.md
  - CV:
      - cv/index.md
  - LLM:
      - llm/index.md
  - Applied AI:
      - applied-ai/index.md
  - Источники: credits.md
```

- [ ] **Step 4: `docs/javascripts/mathjax.js`**

```javascript
window.MathJax = {
  tex: {
    inlineMath: [["\\(", "\\)"]],
    displayMath: [["\\[", "\\]"]],
    processEscapes: true,
    processEnvironments: true,
  },
  options: {
    ignoreHtmlClass: ".*|",
    processHtmlClass: "arithmatex",
  },
};

document$.subscribe(() => {
  MathJax.startup.output.clearCache();
  MathJax.typesetClear();
  MathJax.texReset();
  MathJax.typesetPromise();
});
```

- [ ] **Step 5: `docs/index.md`**

```markdown
# Курсы

Личная программа по 8 направлениям. Каждая тема: теория → самопроверка → задачи с тестами.

| # | Направление | Глубина |
|---|---|---|
| 1 | [Python Advanced](python-advanced/index.md) | 🔴 глубоко |
| 2 | [CS Fundamentals](cs-fundamentals/index.md) | 🟠 уверенно |
| 3 | [Backend Engineering](backend/index.md) | 🔴 глубоко |
| 4 | [Architecture & System Design](architecture/index.md) | 🟠 уверенно |
| 5 | [ML Fundamentals](ml/index.md) | 🟡 повторение |
| 6 | [Computer Vision](cv/index.md) | 🟡 повторение |
| 7 | [LLM Fundamentals](llm/index.md) | 🔴 глубоко |
| 8 | [Applied AI / LLM Engineering](applied-ai/index.md) | 🔴 максимально глубоко |

## Как учиться

1. Прочитай урок, ответь на вопросы самопроверки, не раскрывая ответы.
2. Реши задачи локально (в ветке `work`, не в `main`):

    ```bash
    git clone https://github.com/yarche-tech/courses && cd courses
    git switch -c work
    uv sync
    uv run pytest exercises/python-advanced/01-decorators
    ```

3. Задачам с базой данных нужен `docker compose up -d` (Postgres, Redis).
4. Отметь тему в `PROGRESS.md`.

**Порядок:** инженерный трек 1 → 2 → 3 → 4 и AI-трек 5 + 6 → 7 → 8, параллельно.
```

- [ ] **Step 6: Обзоры разделов** — по одному `docs/<slug>/index.md` на каждый slug. Шаблон (подставить заголовок, глубину, темы и цели из таблицы ниже):

```markdown
# Python Advanced

**Глубина:** 🔴 глубоко

**Цель:** писать идиоматичный и производительный Python, понимать модель исполнения.

## Темы

1. [Декораторы](01-decorators.md)
2. Генераторы и итераторы — *скоро*
3. Контекстные менеджеры — *скоро*
4. ООП и протоколы данных — *скоро*
5. Typing — *скоро*
6. GIL, threading, multiprocessing — *скоро*
7. asyncio — *скоро*
8. Профилирование — *скоро*
9. pytest — *скоро*
```

Содержимое для всех разделов (на этом шаге ссылка `[...](01-decorators.md)` только в python-advanced — до Task 6 её не будет, поэтому в этом шаге пишем «1. Декораторы — *скоро*», ссылку добавляет Task 6):

| slug | Заголовок | Глубина | Цель | Темы |
|---|---|---|---|---|
| python-advanced | Python Advanced | 🔴 глубоко | писать идиоматичный и производительный Python, понимать модель исполнения | Декораторы; Генераторы и итераторы; Контекстные менеджеры; ООП и протоколы данных; Typing; GIL, threading, multiprocessing; asyncio; Профилирование; pytest |
| cs-fundamentals | Computer Science Fundamentals | 🟠 уверенно | уверенно рассуждать о сложности, памяти и сети | Сложность алгоритмов; Структуры данных; Алгоритмы (сортировки, графы, ДП); Память; Процессы и потоки ОС; Сети: TCP/IP; HTTP |
| backend | Backend Engineering | 🔴 глубоко | проектировать и писать надёжные сервисы | REST API; FastAPI; PostgreSQL: модель, индексы, транзакции; Redis; Очереди задач; Кеширование; Безопасность; Тестирование сервисов |
| architecture | Software Architecture & System Design | 🟠 уверенно | проектировать системы и обосновывать компромиссы | Архитектурные паттерны; Распределённые системы; Масштабирование; Отказоустойчивость; Docker; CI/CD; Observability |
| ml | Machine Learning Fundamentals | 🟡 повторение | освежить базу и закрыть пробелы | Математика ML; Классические алгоритмы; Обучение моделей; Метрики; Регуляризация; Оптимизация; PyTorch |
| cv | Computer Vision | 🟡 повторение | освежить базу и закрыть пробелы | OpenCV и обработка изображений; CNN; Детекция; Сегментация; Калибровка камеры |
| llm | LLM Fundamentals | 🔴 глубоко | понимать LLM изнутри — до собственного мини-GPT | Токенизация; Embeddings; Attention и Transformer; Обучение LLM; SFT; LoRA; Quantization; Inference |
| applied-ai | Applied AI / LLM Engineering | 🔴 максимально глубоко | строить продакшн-системы на LLM | RAG; Tool calling; AI-агенты; MCP; Multi-agent системы; Context engineering; LLM Evals; Guardrails; LLMOps |

- [ ] **Step 7: `docs/credits.md`**

```markdown
# Источники

Материалы курсов написаны заново. Код и идеи из источников под MIT используются с указанием авторства.

| Источник | Лицензия | Как используется |
|---|---|---|
| [justxor/python-primery-koda-2026](https://github.com/justxor/python-primery-koda-2026) | MIT | идеи задач и примеры кода |
| [justxor/math-for-ai-2026](https://github.com/justxor/math-for-ai-2026) | MIT | математика для ML/LLM |
| Прочие репозитории [justxor](https://github.com/justxor) | без лицензии | только как ориентир по темам; текст не копируется |
```

- [ ] **Step 8: Тесты и сборка**

Run: `uv run pytest tests/test_structure.py -v && uv run mkdocs build --strict`
Expected: тесты passed (`test_lesson_front_matter` пока без параметров — 0 случаев); сборка без предупреждений, создан `site/`; `ls site | grep superpowers` пусто.

- [ ] **Step 9: Commit**

```bash
git add mkdocs.yml docs/index.md docs/credits.md docs/javascripts docs/*/index.md tests/test_structure.py
git commit -m "feat: каркас сайта — 8 разделов на MkDocs Material"
```

---

### Task 6: Урок «Декораторы»

**Files:**
- Create: `docs/python-advanced/01-decorators.md`
- Modify: `docs/python-advanced/index.md` (ссылка на урок), `mkdocs.yml` (nav)

**Interfaces:**
- Consumes: задачи из Task 4 (имена `count_calls`, `retry`, `enforce_types`), тест `test_lesson_front_matter` из Task 5.

- [ ] **Step 1: Проверить, что тест на урок появится** — создать файл только с front matter без `sources`:

```markdown
---
title: Декораторы
status: draft
---
```

Run: `uv run pytest tests/test_structure.py -k front_matter -v`
Expected: `test_lesson_front_matter[01-decorators]` FAILED («нет sources»).

- [ ] **Step 2: Написать урок полностью.** Front matter:

```yaml
---
title: Декораторы
status: reviewed
sources:
  - https://docs.python.org/3/glossary.html#term-decorator
  - https://peps.python.org/pep-0318/
  - https://docs.python.org/3/library/functools.html#functools.wraps
  - https://github.com/justxor/python-primery-koda-2026 (MIT)
---
```

Обязательные разделы и содержание (текст писать своими словами, код — рабочий, Python 3.13):

1. `# Декораторы`, затем `## Зачем` — сквозная логика (логирование, ретраи, кеш, права), не трогая тело функции.
2. `## Функции — объекты первого класса` — присваивание, передача, возврат функции; замыкание и `__closure__`; `nonlocal`.
3. `## Синтаксис @` — `@d def f` ≡ `f = d(f)`; порядок применения нескольких декораторов (снизу вверх) с примером, печатающим порядок.
4. `## functools.wraps` — что теряется без него (`__name__`, `__doc__`, `__wrapped__`, `inspect.signature`), пример до/после.
5. `## Декораторы с параметрами` — три уровня вложенности (фабрика → декоратор → обёртка); пример `repeat(n)`.
6. `## Состояние декоратора` — атрибут на обёртке vs `nonlocal` vs класс с `__call__`; пример класса-декоратора.
7. `## Декораторы классов и методов` — `@dataclass`, `@property`, `@classmethod`/`@staticmethod` как встроенные примеры; `@functools.cache`/`lru_cache`; декоратор, применённый к методу (self попадает в `*args`).
8. `## Подводные камни` (admonition `!!! warning`) — забытый `return` в обёртке; декоратор выполняется при импорте; мутабельное состояние, общее для всех вызовов; `lru_cache` на методе держит `self`; потеря сигнатуры без `wraps`; async-функции: обёртка должна быть `async def` и делать `await`.
9. `## Самопроверка` — 8 вопросов, каждый в виде:

```markdown
??? question "Что выведет код? …"
    Ответ: …
```

Вопросы: (1) во что раскрывается `@a @b def f`, порядок применения; (2) когда выполняется код декоратора — при импорте или при вызове; (3) что сломается без `functools.wraps` (назвать 3 вещи); (4) зачем три уровня функций у декоратора с параметрами; (5) почему `@retry` без скобок у декоратора с параметрами ломается и как сделать декоратор, работающий и с `()`, и без; (6) чем `lru_cache` на методе опасен для памяти; (7) как написать декоратор для `async def`; (8) как получить исходную функцию из задекорированной.

10. `## Практика` — три задачи (`count_calls`, `retry`, `enforce_types`) с 1–2 предложениями условия каждая, ссылка на папку `https://github.com/yarche-tech/courses/tree/main/exercises/python-advanced/01-decorators` и команда `uv run pytest exercises/python-advanced/01-decorators`.
11. `## Дальше` — ссылки: глоссарий Python (decorator), PEP 318, PEP 3129 (декораторы классов), документация `functools`, лекция CS центра по Python (Сергей Лебедев, «Декораторы»).

- [ ] **Step 3: Подключить урок**

В `mkdocs.yml` раздел nav:

```yaml
  - Python Advanced:
      - python-advanced/index.md
      - Декораторы: python-advanced/01-decorators.md
```

В `docs/python-advanced/index.md` заменить `1. Декораторы — *скоро*` на `1. [Декораторы](01-decorators.md)`.

- [ ] **Step 4: Проверить код из урока** — каждый блок ```python без `...` скопировать и выполнить:

Run: `uv run python - <<'EOF'` + содержимое блока + `EOF` для каждого блока (или `uv run python -c`).
Expected: блоки выполняются без исключений, вывод совпадает с указанным в уроке.

- [ ] **Step 5: Тесты и сборка**

Run: `uv run pytest -v && uv run mkdocs build --strict`
Expected: все тесты passed, включая `test_lesson_front_matter[01-decorators]`; сборка без предупреждений.

- [ ] **Step 6: Просмотр** — `uv run mkdocs serve`, открыть `http://127.0.0.1:8000/courses/python-advanced/01-decorators/`: вкладки разделов, раскрывающиеся ответы, подсветка кода, поиск по слову «декоратор» находит урок, тёмная тема переключается.

- [ ] **Step 7: Commit**

```bash
git add docs/python-advanced mkdocs.yml
git commit -m "feat: урок «Декораторы»"
```

---

### Task 7: README, CLAUDE.md, PROGRESS.md

**Files:**
- Create: `README.md`, `CLAUDE.md`, `PROGRESS.md`

- [ ] **Step 1: `README.md`**

```markdown
# Курсы

Сайт: https://yarche-tech.github.io/courses/

## Быстрый старт

    uv sync
    uv run mkdocs serve          # сайт локально: http://127.0.0.1:8000/courses/
    git switch -c work           # решения — только в ветке work, не в main
    uv run pytest exercises/python-advanced/01-decorators

Задачам с БД: `docker compose up -d`. Если порты 5432/6379 заняты —
`COURSES_PG_PORT=5433 docker compose up -d` и `COURSES_PG_DSN=postgresql://courses:courses@localhost:5433/courses`.

## Структура

- `docs/` — сайт (уроки), `docs/superpowers/` — спеки и планы, не публикуются
- `exercises/` — заготовки и тесты, `solutions/` — эталоны
- `tests/` — проверки самого репозитория: `uv run pytest`

В ветке `work` с твоими решениями `tests/test_exercises.py::test_stub_fails` упадёт — это ожидаемо;
там запускай только `uv run pytest exercises/...`.
```

- [ ] **Step 2: `CLAUDE.md`** — правила для будущих сессий:

```markdown
# Правила репозитория курсов

- Новая тема = урок `docs/<slug>/NN-<topic>.md` + `exercises/<slug>/NN-<topic>/{task.py,test_task.py,README.md}`
  + `solutions/<slug>/NN-<topic>/task.py` + строка в nav `mkdocs.yml` + ссылка в `docs/<slug>/index.md` + пункт в `PROGRESS.md`.
- Front matter урока: `title`, `status: draft|reviewed`, `sources: [...]`. `reviewed` — только после проверки точности.
- Структура урока: Зачем → теория → Подводные камни → Самопроверка (`??? question`) → Практика → Дальше.
- Тесты упражнений используют только фикстуру `task`; БД — фикстуры `pg_dsn`, `redis_url`.
- Заготовка: функции с `raise NotImplementedError`; на ней тесты должны падать, на эталоне — проходить.
- Репозитории justxor без лицензии — только ориентир по темам, текст не копировать. MIT — с указанием в `sources` и `docs/credits.md`.
- Перед коммитом: `uv run pytest && uv run mkdocs build --strict`.
```

- [ ] **Step 3: `PROGRESS.md`** — чек-лист всех тем из таблицы Task 5, по разделам:

```markdown
# Прогресс

## Python Advanced
- [ ] Декораторы
- [ ] Генераторы и итераторы
...
```

(Все темы всех 8 разделов из таблицы Task 5, по одной строке.)

- [ ] **Step 4: Проверить и закоммитить**

Run: `uv run pytest && uv run mkdocs build --strict`
Expected: всё зелёное.

```bash
git add README.md CLAUDE.md PROGRESS.md
git commit -m "docs: README, правила добавления тем, прогресс"
```

---

### Task 8: CI — тесты и деплой сайта

**Files:**
- Create: `.github/workflows/tests.yml`, `.github/workflows/site.yml`

- [ ] **Step 1: `.github/workflows/tests.yml`**

```yaml
name: tests
on:
  push:
  pull_request:

jobs:
  tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_USER: courses
          POSTGRES_PASSWORD: courses
          POSTGRES_DB: courses
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U courses" --health-interval 5s
          --health-timeout 5s --health-retries 10
      redis:
        image: redis:7
        ports: ["6379:6379"]
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv sync
      - run: uv run pytest -v
```

- [ ] **Step 2: `.github/workflows/site.yml`**

```yaml
name: site
on:
  push:
    branches: [main]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v6
      - run: uv sync --group docs
      - run: uv run mkdocs build --strict
      - uses: actions/upload-pages-artifact@v3
        with:
          path: site
  deploy:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - id: deployment
        uses: actions/deploy-pages@v4
```

- [ ] **Step 3: Проверить YAML локально**

Run: `uv run python -c "import yaml,sys; [yaml.safe_load(open(f)) for f in sys.argv[1:]]; print('ok')" .github/workflows/*.yml`
Expected: `ok`.

- [ ] **Step 4: Commit**

```bash
git add .github
git commit -m "ci: тесты и деплой сайта на GitHub Pages"
```

---

### Task 9: Публикация (требует подтверждения пользователя)

Внешнее действие: создаёт публичный репозиторий. Перед Step 1 — явное «да» пользователя в чате.

- [ ] **Step 1: Создать репо и запушить**

```bash
gh repo create yarche-tech/courses --public --source . --remote origin --push
```

- [ ] **Step 2: Включить Pages из Actions**

```bash
gh api -X POST repos/yarche-tech/courses/pages -f build_type=workflow
```

Expected: JSON с `"build_type": "workflow"`. Если 409 (уже включено) — `gh api -X PUT repos/yarche-tech/courses/pages -f build_type=workflow`.

- [ ] **Step 3: Перезапустить деплой и дождаться**

```bash
gh workflow run site.yml
gh run watch $(gh run list --workflow site.yml --limit 1 --json databaseId -q '.[0].databaseId') --exit-status
gh run list --workflow tests.yml --limit 1
```

Expected: `site` и `tests` — success.

- [ ] **Step 4: Проверить сайт**

Run: `curl -sf https://yarche-tech.github.io/courses/python-advanced/01-decorators/ | grep -c "Декораторы"`
Expected: число > 0. Открыть в браузере, проверить главную и урок.
