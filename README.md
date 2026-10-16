# Курсы

Сайт: https://yarche-tech.github.io/courses/

## Быстрый старт

```bash
uv sync
uv run mkdocs serve          # сайт локально: http://127.0.0.1:8000/courses/
git switch -c work           # решения — только в ветке work, не в main
uv run pytest exercises/python-advanced/01-decorators
```

Задачам с БД: `docker compose up -d`. Если порты 5432/6379 заняты —
`COURSES_PG_PORT=5433 docker compose up -d` и `COURSES_PG_DSN=postgresql://courses:courses@localhost:5433/courses`
(для Redis — `COURSES_REDIS_PORT` и `COURSES_REDIS_URL`).

## Структура

- `docs/` — сайт (уроки), `docs/superpowers/` — спеки и планы, не публикуются
- `exercises/` — заготовки и тесты, `solutions/` — эталоны
- `tests/` — проверки самого репозитория: `uv run pytest`

В ветке `work` с твоими решениями `tests/test_exercises.py::test_stub_fails` упадёт — это ожидаемо;
там запускай только `uv run pytest exercises/...`.
