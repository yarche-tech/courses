from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_site_build_runs_structure_tests_before_build():
    workflow = yaml.safe_load((ROOT / ".github/workflows/site.yml").read_text(encoding="utf-8"))
    runs = [step.get("run", "") for step in workflow["jobs"]["build"]["steps"]]
    tests = next(i for i, r in enumerate(runs) if "pytest tests/test_structure.py" in r)
    build = next(i for i, r in enumerate(runs) if "mkdocs build" in r)
    assert tests < build, "битый урок не должен попасть на сайт: тесты структуры — до сборки"
