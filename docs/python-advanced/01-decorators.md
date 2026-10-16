---
title: Декораторы
status: reviewed
sources:
  - https://docs.python.org/3/glossary.html#term-decorator
  - https://peps.python.org/pep-0318/
  - https://docs.python.org/3/library/functools.html#functools.wraps
  - https://github.com/justxor/python-primery-koda-2026 (MIT)
---

# Декораторы

## Зачем

Часть логики нужна многим функциям сразу: логирование, повтор при сетевой ошибке,
кеширование, проверка прав, замер времени. Копировать её в каждую функцию плохо.
Декоратор позволяет **обернуть** функцию дополнительным поведением, не трогая её тело:

```python
@retry(3)
def fetch_user(user_id): ...
```

Читатель сразу видит, что функция повторяется при ошибках, а сама она остаётся
про бизнес-логику.

## Функции — объекты первого класса

В Python функция — обычный объект. Её можно присвоить переменной, передать
аргументом и вернуть из другой функции.

```python
def shout(text):
    return text.upper()

say = shout                       # присвоили
print(say("привет"))              # ПРИВЕТ


def apply(func, value):           # передали аргументом
    return func(value)

print(apply(len, "абв"))          # 3


def make_multiplier(k):           # вернули из функции
    def multiply(x):
        return x * k
    return multiply

triple = make_multiplier(3)
print(triple(5))                  # 15
```

`multiply` помнит `k`, хотя `make_multiplier` уже завершилась. Это **замыкание**:
вложенная функция захватывает переменные объемлющей области. Захваченные значения
лежат в ячейках `__closure__`:

```python
def make_multiplier(k):
    def multiply(x):
        return x * k
    return multiply

triple = make_multiplier(3)
print(triple.__closure__[0].cell_contents)   # 3
```

Чтобы **изменить** захваченную переменную, а не создать локальную, нужен `nonlocal`:

```python
def make_counter():
    count = 0
    def inc():
        nonlocal count
        count += 1
        return count
    return inc

c = make_counter()
c(); c()
print(c())   # 3
```

Без `nonlocal` строка `count += 1` упадёт с `UnboundLocalError`: присваивание
делает `count` локальной для `inc`.

## Синтаксис `@`

Декоратор — это вызываемый объект, который принимает функцию и возвращает
(обычно другую) функцию. Запись

```python
@decorator
def f(): ...
```

ровно эквивалентна `f = decorator(f)`. Простейший декоратор:

```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"вызов {func.__name__}{args}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def add(a, b):
    return a + b

print(add(2, 3))
# вызов add(2, 3)
# 5
```

`*args, **kwargs` в обёртке пропускают любые аргументы, а `return` возвращает
результат исходной функции.

Несколько декораторов применяются **снизу вверх**: ближайший к `def` — первым.
А при вызове обёртки выполняются сверху вниз:

```python
def tag(name):
    def decorator(func):
        print(f"применяю {name}")
        def wrapper():
            return f"<{name}>{func()}</{name}>"
        return wrapper
    return decorator

@tag("b")
@tag("i")
def hello():
    return "привет"
# применяю i
# применяю b

print(hello())   # <b><i>привет</i></b>
```

То есть `hello = tag("b")(tag("i")(hello))`.

## `functools.wraps`

Обёртка — это другая функция, поэтому без дополнительных усилий теряются
имя, докстринг и сигнатура оригинала:

```python
import inspect

def plain(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@plain
def area(width: float, height: float) -> float:
    """Площадь прямоугольника."""
    return width * height

print(area.__name__)            # wrapper
print(area.__doc__)             # None
print(inspect.signature(area))  # (*args, **kwargs)
```

Это ломает отладку, документацию, `help()`, фреймворки, которые читают сигнатуру
(FastAPI, pytest-фикстуры, click). `functools.wraps` копирует метаданные
(`__module__`, `__name__`, `__qualname__`, `__doc__`, `__annotations__`,
`__type_params__`), дополняет `__dict__` обёртки атрибутами оригинала и добавляет
`__wrapped__` — ссылку на оригинал. `inspect.signature` идёт по `__wrapped__`
и показывает настоящую сигнатуру:

```python
import functools
import inspect

def proper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@proper
def area(width: float, height: float) -> float:
    """Площадь прямоугольника."""
    return width * height

print(area.__name__)              # area
print(area.__doc__)               # Площадь прямоугольника.
print(inspect.signature(area))    # (width: float, height: float) -> float
print(area.__wrapped__(2, 3))     # 6
```

Правило: **в каждой обёртке — `@functools.wraps(func)`**.

## Декораторы с параметрами

`@retry(3)` — это сначала вызов `retry(3)`, который **возвращает декоратор**,
и только он применяется к функции. Получается три уровня:

1. **фабрика** принимает параметры;
2. **декоратор** принимает функцию;
3. **обёртка** принимает аргументы вызова.

```python
import functools

def repeat(n):                         # 1. фабрика
    def decorator(func):               # 2. декоратор
        @functools.wraps(func)
        def wrapper(*args, **kwargs):  # 3. обёртка
            result = None
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def ping():
    print("ping")

ping()
# ping
# ping
# ping
```

Частая ошибка — написать `@repeat` без скобок. Тогда `repeat` получит функцию
вместо `n`, вернёт `decorator`, и `ping()` превратится в вызов `decorator()`
без аргументов → `TypeError`.

Если хочется, чтобы декоратор работал и с `()`, и без, используют ключевые
параметры и проверку первого аргумента:

```python
import functools

def debug(func=None, *, prefix="DEBUG"):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            print(f"{prefix}: {f.__name__}")
            return f(*args, **kwargs)
        return wrapper
    if func is None:          # вызвали как @debug(prefix=...)
        return decorator
    return decorator(func)    # вызвали как @debug

@debug
def a(): pass

@debug(prefix="TRACE")
def b(): pass

a()   # DEBUG: a
b()   # TRACE: b
```

## Состояние декоратора

Декоратору часто нужно что-то помнить: число вызовов, кеш, время последнего
запуска. Три способа:

**Атрибут на обёртке** — состояние видно снаружи (`f.calls`). Так устроена
задача `count_calls`.

**`nonlocal` в замыкании** — состояние скрыто:

```python
import functools

def once(func):
    """Вызывает func только первый раз, дальше возвращает сохранённый результат."""
    done = False
    result = None

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal done, result
        if not done:
            result = func(*args, **kwargs)
            done = True
        return result
    return wrapper

@once
def init():
    print("инициализация")
    return 42

print(init(), init())
# инициализация
# 42 42
```

**Класс с `__call__`** — удобно, когда состояния и методов много:

```python
import functools

class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)

@CountCalls
def hello():
    return "hi"

hello(); hello()
print(hello.calls, hello.__name__)   # 2 hello
```

Минус класса: экземпляр не является дескриптором, поэтому на **методе** класса
такой декоратор не получит `self` без дополнительного `__get__`. Функции-обёртки
этой проблемы не имеют.

## Декораторы классов и методов

Многие встроенные инструменты — декораторы:

- `@property`, `@classmethod`, `@staticmethod` — меняют то, как атрибут класса
  ведёт себя при обращении;
- `@dataclasses.dataclass` — **декоратор класса** (PEP 3129): получает класс,
  дописывает `__init__`, `__repr__`, `__eq__` и возвращает его;
- `@functools.cache` и `@functools.lru_cache(maxsize=...)` — мемоизация.

```python
import functools

@functools.lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(80))             # 23416728348467685
print(fib.cache_info())    # CacheInfo(hits=78, misses=81, maxsize=None, currsize=81)
```

Обычный функциональный декоратор работает и на методах: `self` просто приходит
первым элементом `*args`.

```python
import functools

def log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"{func.__qualname__} args={args[1:]}")
        return func(*args, **kwargs)
    return wrapper

class Account:
    def __init__(self):
        self.balance = 0

    @log
    def deposit(self, amount):
        self.balance += amount

acc = Account()
acc.deposit(100)          # Account.deposit args=(100,)
print(acc.balance)        # 100
```

## Подводные камни

!!! warning "Частые ошибки"
    - **Забытый `return` в обёртке.** Функция «работает», но всегда возвращает `None`.
    - **Код декоратора выполняется при импорте модуля**, а не при вызове функции.
      Тяжёлые действия (подключение к БД, чтение файлов) в теле декоратора
      замедляют импорт и выполняются, даже если функция не понадобится.
    - **Общее изменяемое состояние.** Список или словарь в замыкании декоратора
      общий для всех вызовов и, если декоратор с параметрами создаёт его на уровне
      фабрики, — для всех функций, задекорированных одной фабрикой.
    - **`lru_cache` на методе держит `self`** в кеше: объекты не освобождаются,
      пока живёт кеш. Для методов — `functools.cached_property` или кеш на экземпляре.
    - **Без `functools.wraps` теряется сигнатура** — ломаются фреймворки,
      которые её читают (FastAPI, pytest, click).
    - **`async def` под обычной обёрткой.** Обёртка вернёт корутину, не дождавшись
      её: время, ретраи, логирование результата будут неверными. Для асинхронных
      функций обёртка тоже должна быть `async def` и делать `await func(...)`.

Пример корректного асинхронного декоратора:

```python
import asyncio
import functools
import time

def timed(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            print(f"{func.__name__}: {time.perf_counter() - start:.2f} с")
    return wrapper

@timed
async def work():
    await asyncio.sleep(0.1)
    return "готово"

print(asyncio.run(work()))
# work: 0.10 с
# готово
```

## Самопроверка

??? question "Во что раскрывается `@a` над `@b` над `def f`? Какой декоратор применяется первым?"
    `f = a(b(f))`. Первым применяется `b` — ближайший к `def`. При вызове
    первой выполняется обёртка `a`, внутри неё — обёртка `b`, внутри — `f`.

??? question "Когда выполняется код декоратора — при импорте модуля или при вызове функции?"
    Тело декоратора (всё, что вне обёртки) — один раз, при определении функции,
    то есть обычно при импорте модуля. Тело обёртки — при каждом вызове.

??? question "Что сломается без `functools.wraps`? Назови три вещи."
    `__name__` станет `wrapper`, `__qualname__` — `plain.<locals>.wrapper`, пропадёт `__doc__`,
    `inspect.signature` покажет `(*args, **kwargs)`, не будет `__wrapped__`.
    Следствия: непонятные трейсбеки и логи, сломанный `help()`, фреймворки
    (FastAPI, pytest, click) не видят настоящие параметры.

??? question "Зачем у декоратора с параметрами три уровня функций?"
    `@retry(3)` сначала вызывает `retry(3)` — это уровень параметров. Он должен
    вернуть настоящий декоратор (уровень функции), который вернёт обёртку
    (уровень аргументов вызова). Каждый уровень принимает своё: параметры,
    функцию, аргументы.

??? question "Почему `@retry` без скобок у декоратора с параметрами ломается и как сделать декоратор, работающий в обоих вариантах?"
    Без скобок `retry` получит функцию как значение `times`. Если параметры
    не проверяются, вернётся внутренний декоратор вместо обёртки, и вызов функции
    станет вызовом декоратора без аргументов → `TypeError`. Если фабрика проверяет
    параметры (как `retry` из задачи: `times < 1`), ошибка случится раньше —
    ещё при декорировании: сравнение функции с числом даёт `TypeError`. Решение: `def deco(func=None, *, опции)`:
    если `func is None` — вернуть декоратор, иначе сразу применить его к `func`.

??? question "Чем `@lru_cache` на методе опасен для памяти?"
    `self` — часть ключа кеша, поэтому кеш держит сильные ссылки на все
    экземпляры, у которых вызывали метод. Они не будут собраны сборщиком мусора,
    пока жив кеш (обычно — пока жив класс). Лучше `functools.cached_property`
    или кеш в атрибуте экземпляра.

??? question "Как написать декоратор для `async def`-функции?"
    Обёртка сама должна быть `async def` и вызывать `await func(*args, **kwargs)`,
    плюс `@functools.wraps(func)`. Универсальный декоратор проверяет
    `inspect.iscoroutinefunction(func)` и возвращает синхронную или асинхронную обёртку.

??? question "Как получить исходную функцию из задекорированной?"
    Через `f.__wrapped__` (если декоратор использовал `functools.wraps`).
    Для цепочки декораторов — `inspect.unwrap(f)`, который идёт по `__wrapped__` до конца.

## Практика

Задачи: [exercises/python-advanced/01-decorators](https://github.com/yarche-tech/courses/tree/main/exercises/python-advanced/01-decorators)

1. **`count_calls`** — декоратор считает вызовы в атрибуте `calls`, включая
   неудачные, и сохраняет метаданные функции.
2. **`retry(times, exceptions, delay, sleep)`** — декоратор с параметрами:
   повторяет вызов при заданных исключениях, между попытками спит, после
   последней попытки пробрасывает исключение.
3. **`enforce_types`** — проверяет аргументы и результат по аннотациям-классам
   через `inspect.signature` и `typing.get_type_hints`.

```bash
uv run pytest exercises/python-advanced/01-decorators
```

## Дальше

- [Глоссарий Python: decorator](https://docs.python.org/3/glossary.html#term-decorator)
- [PEP 318 — декораторы функций и методов](https://peps.python.org/pep-0318/)
- [PEP 3129 — декораторы классов](https://peps.python.org/pep-3129/)
- [Документация `functools`](https://docs.python.org/3/library/functools.html)
- Лекция Computer Science Center по Python (Сергей Лебедев) «Декораторы» — на YouTube
