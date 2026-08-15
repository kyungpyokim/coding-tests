from typing import Any, Generic, Protocol, TypeVar, overload, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class Serializable(Protocol):
    def to_dict(self) -> dict[str, Any]: ...


@runtime_checkable
class Renderable(Protocol):
    def render_html(self) -> str: ...


class GenericStack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        if not self._items:
            raise IndexError("pop from empty stack")
        return self._items.pop()

    def peek(self) -> T:
        if not self._items:
            raise IndexError("peek from empty stack")
        return self._items[-1]

    def __len__(self) -> int:
        return len(self._items)


@overload
def format_output(value: int) -> str: ...


@overload
def format_output(value: list[str]) -> int: ...


@overload
def format_output(value: Serializable) -> dict[str, Any]: ...


def format_output(value: Any) -> Any:
    if isinstance(value, bool):  # Note: bool is subclass of int in Python
        raise TypeError("Boolean is not supported")
    if isinstance(value, int):
        return f"NUM:{value}"
    if isinstance(value, list) and all(isinstance(x, str) for x in value):
        return sum(len(x) for x in value)
    if isinstance(value, Serializable):
        return value.to_dict()
    raise TypeError(f"Unsupported type: {type(value).__name__}")
