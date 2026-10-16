import pytest


# --- Задача 1: count_calls ---------------------------------------------------

def test_count_calls_counts(task):
    @task.count_calls
    def add(a, b):
        return a + b

    assert add.calls == 0
    assert add(1, 2) == 3
    add(3, 4)
    assert add.calls == 2


def test_count_calls_independent_counters(task):
    @task.count_calls
    def f():
        pass

    @task.count_calls
    def g():
        pass

    f(); f(); g()
    assert (f.calls, g.calls) == (2, 1)


def test_count_calls_keeps_metadata(task):
    @task.count_calls
    def documented(x: int) -> int:
        """Док."""
        return x

    assert documented.__name__ == "documented"
    assert documented.__doc__ == "Док."
    assert documented.__wrapped__(5) == 5


def test_count_calls_counts_failed_calls(task):
    @task.count_calls
    def boom():
        raise ValueError

    with pytest.raises(ValueError):
        boom()
    assert boom.calls == 1


# --- Задача 2: retry ---------------------------------------------------------

def make_flaky(fail_times: int, exc: type[Exception] = ConnectionError):
    state = {"calls": 0}

    def flaky():
        state["calls"] += 1
        if state["calls"] <= fail_times:
            raise exc("fail")
        return "ok"

    return flaky, state


def test_retry_succeeds_after_failures(task):
    sleeps: list[float] = []
    flaky, state = make_flaky(2)
    wrapped = task.retry(3, delay=0.5, sleep=sleeps.append)(flaky)
    assert wrapped() == "ok"
    assert state["calls"] == 3
    assert sleeps == [0.5, 0.5]


def test_retry_reraises_last_after_exhausting(task):
    sleeps: list[float] = []
    flaky, state = make_flaky(10)
    wrapped = task.retry(3, sleep=sleeps.append)(flaky)
    with pytest.raises(ConnectionError):
        wrapped()
    assert state["calls"] == 3
    assert len(sleeps) == 2  # после последней попытки не спим


def test_retry_does_not_catch_other_exceptions(task):
    flaky, state = make_flaky(1, exc=KeyError)
    wrapped = task.retry(3, exceptions=(ConnectionError,), sleep=lambda s: None)(flaky)
    with pytest.raises(KeyError):
        wrapped()
    assert state["calls"] == 1


def test_retry_passes_arguments_and_keeps_name(task):
    @task.retry(2, sleep=lambda s: None)
    def mul(a, *, b):
        return a * b

    assert mul(3, b=4) == 12
    assert mul.__name__ == "mul"


@pytest.mark.parametrize("times", [0, -1])
def test_retry_rejects_non_positive_times(task, times):
    with pytest.raises(ValueError):
        task.retry(times)


# --- Задача 3: enforce_types -------------------------------------------------

def test_enforce_types_accepts_valid(task):
    @task.enforce_types
    def greet(name: str, times: int = 1) -> str:
        return name * times

    assert greet("a", 3) == "aaa"
    assert greet(name="b") == "b"


def test_enforce_types_rejects_bad_argument(task):
    @task.enforce_types
    def greet(name: str, times: int = 1) -> str:
        return name * times

    with pytest.raises(TypeError, match="times"):
        greet("a", "3")


def test_enforce_types_checks_return(task):
    @task.enforce_types
    def broken() -> int:
        return "not int"

    with pytest.raises(TypeError, match="return"):
        broken()


def test_enforce_types_ignores_unannotated_and_generics(task):
    @task.enforce_types
    def f(a, items: list[int]) -> None:
        return None

    assert f(object(), ["x"]) is None


def test_enforce_types_keeps_name(task):
    @task.enforce_types
    def named(x: int) -> int:
        return x

    assert named.__name__ == "named"
