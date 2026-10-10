"""Decorators for measuring execution time, logging, and operation tracking."""

from collections import deque
from functools import wraps
from time import perf_counter
from typing import Any, Callable

# Global deque tracking last operations (Advanced Task #7)
operation_history: deque[str] = deque(maxlen=20)


def measure_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to measure and display execution time of a function."""
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = perf_counter()
        result = func(*args, **kwargs)
        elapsed = perf_counter() - start_time
        print(f"[TIMING] {func.__name__}: {elapsed:.8f} s")
        operation_history.append(f"{func.__name__} executed in {elapsed:.8f} s")
        return result
    return wrapper


def repeat(count: int = 1) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Parameterized decorator (Advanced Task #3) combining closure, decorator, *args, **kwargs."""
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = None
            for _ in range(count):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator
