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
