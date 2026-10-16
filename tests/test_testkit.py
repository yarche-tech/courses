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
