from typing import Any, Generic, Protocol, TypeVar, overload, runtime_checkable

T = TypeVar("T")


@runtime_checkable
class Serializable(Protocol):
    """Structural Subtyping Protocol for objects convertible to dict."""

    def to_dict(self) -> dict[str, Any]:
        """Convert object state to dict."""
        ...


@runtime_checkable
class Renderable(Protocol):
    """Protocol for objects that can render HTML."""

    def render_html(self) -> str:
        """Render to HTML string."""
        ...


class GenericStack(Generic[T]):
    """Type-safe Generic Stack implementation."""

    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        # TODO: item을 스택에 추가하세요.
        raise NotImplementedError

    def pop(self) -> T:
        """Pop and return top item. Raises IndexError if empty."""
        # TODO: 스택 최상단 요소를 꺼내 반환하세요.
        raise NotImplementedError

    def peek(self) -> T:
        """Return top item without removing. Raises IndexError if empty."""
        # TODO: 스택 최상단 요소를 조회하세요.
        raise NotImplementedError

    def __len__(self) -> int:
        # TODO: 스택 길이 반환.
        raise NotImplementedError


# Static Type Overloading
@overload
def format_output(value: int) -> str: ...


@overload
def format_output(value: list[str]) -> int: ...


@overload
def format_output(value: Serializable) -> dict[str, Any]: ...


def format_output(value: Any) -> Any:
    """Polymorphic formatter with static typing overloads.

    - If int: returns f"NUM:{value}"
    - If list of strings: returns total character length across all strings
    - If matches Serializable protocol: returns value.to_dict()
    - Otherwise: raises TypeError
    """
    # TODO: 타입 검사 및 적절한 포맷 결과를 반환하세요.
    raise NotImplementedError
