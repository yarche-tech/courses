"""Эталон проходит тесты, заготовка — нет. Ловит «решение в заготовке» и сломанные тесты."""

import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
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


def stub_counts(exercise_dir: Path, cwd: Path = ROOT) -> tuple[int, int]:
    """(прошло, упало) на заготовке. Любой прошедший тест — утечка решения."""
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "report.xml"
        env = {**os.environ, "COURSES_SOLUTIONS": "0"}
        subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             f"--junitxml={report}", str(exercise_dir)],
            cwd=cwd, env=env, capture_output=True, text=True,
        )
        suite = ET.parse(report).getroot().find("testsuite")
    failed = int(suite.get("failures")) + int(suite.get("errors"))
    passed = int(suite.get("tests")) - failed - int(suite.get("skipped"))
    return passed, failed


def test_there_are_exercises():
    assert EXERCISES, "нет ни одного упражнения"


@pytest.mark.parametrize("exercise_dir", EXERCISES, ids=IDS)
def test_solution_passes(exercise_dir):
    result = run_pytest(exercise_dir, solutions=True)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("exercise_dir", EXERCISES, ids=IDS)
def test_stub_fails(exercise_dir):
    passed, failed = stub_counts(exercise_dir)
    assert passed == 0, f"на заготовке прошло тестов: {passed} — решение попало в exercises/"
    assert failed > 0


def test_solution_passes_from_exercise_dir():
    exercise_dir = EXERCISES[0]
    result = run_pytest(Path("."), solutions=True, cwd=exercise_dir)
    assert result.returncode == 0, result.stdout + result.stderr


def test_partial_leak_is_detected(tmp_path):
    for name in ("conftest.py", "pyproject.toml"):
        (tmp_path / name).write_text((ROOT / name).read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "testkit").mkdir()
    (tmp_path / "testkit" / "__init__.py").write_text(
        (ROOT / "testkit" / "__init__.py").read_text(encoding="utf-8"), encoding="utf-8")
    exercise = tmp_path / "exercises" / "a" / "01-x"
    exercise.mkdir(parents=True)
    (exercise / "task.py").write_text(
        "def solved():\n    return 1\n\ndef unsolved():\n    raise NotImplementedError\n", encoding="utf-8")
    (exercise / "test_task.py").write_text(
        "def test_solved(task):\n    assert task.solved() == 1\n\n"
        "def test_unsolved(task):\n    assert task.unsolved() == 2\n", encoding="utf-8")
    assert stub_counts(exercise, cwd=tmp_path) == (1, 1)
