# Правила репозитория курсов

- Новая тема = урок `docs/<slug>/NN-<topic>.md` + `exercises/<slug>/NN-<topic>/{task.py,test_task.py,README.md}`
  + `solutions/<slug>/NN-<topic>/task.py` + строка в nav `mkdocs.yml` + ссылка в `docs/<slug>/index.md` + пункт в `PROGRESS.md`.
- Front matter урока: `title`, `status: draft|reviewed`, `sources: [...]`. `reviewed` — только после проверки точности.
- Структура урока: Зачем → теория → Подводные камни → Самопроверка (`??? question`) → Практика → Дальше.
- Код в уроке должен выполняться; вывод в комментариях — реальный.
- Тесты упражнений используют только фикстуру `task`; БД — фикстуры `pg_dsn`, `redis_url`.
- Заготовка: функции с `raise NotImplementedError`; на ней тесты должны падать, на эталоне — проходить.
- Репозитории justxor без лицензии — только ориентир по темам, текст не копировать. MIT — с указанием в `sources` и `docs/credits.md`.
- MkDocs закреплён `<2`: MkDocs 2.0 несовместим с Material.
- Перед коммитом: `uv run pytest && uv run mkdocs build --strict`.
