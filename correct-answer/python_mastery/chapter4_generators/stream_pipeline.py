import functools
from collections.abc import Callable, Generator, Iterator, Mapping
from typing import Any, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def flatten_tree(tree: Any) -> Iterator[Any]:
    if isinstance(tree, (list, tuple, set)):
        for item in tree:
            yield from flatten_tree(item)
    elif isinstance(tree, Mapping):
        for val in tree.values():
            yield from flatten_tree(val)
    else:
        yield tree


def coroutine(
    func: Callable[..., Generator[R, T, Any]],
) -> Callable[..., Generator[R, T, Any]]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Generator[R, T, Any]:
        gen = func(*args, **kwargs)
        next(gen)  # Prime coroutine
        return gen

    return wrapper


class ResetSignal(Exception):
    """Signal exception sent via .throw() to reset coroutine state."""


def averager() -> Generator[tuple[int, float], float, tuple[int, float]]:
    total = 0.0
    count = 0
    avg = 0.0
    while True:
        try:
            val = yield (count, avg)
            total += val
            count += 1
            avg = total / count
        except ResetSignal:
            total = 0.0
            count = 0
            avg = 0.0
        except GeneratorExit:
            return (count, avg)


@coroutine
def pipeline_broadcast(
    targets: list[Generator[None, Any, Any]],
) -> Generator[None, Any, None]:
    while True:
        item = yield
        for target in targets:
            target.send(item)
