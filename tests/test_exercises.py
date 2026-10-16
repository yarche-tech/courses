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
