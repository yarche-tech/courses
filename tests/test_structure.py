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
