import re
from pathlib import Path

import pytest
import yaml

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
