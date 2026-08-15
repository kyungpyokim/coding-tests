from collections.abc import Iterator
from contextlib import ExitStack, contextmanager
from typing import Any


class MockResource:
    def __init__(self, name: str) -> None:
        self.name = name
        self.is_open = False

    def open(self) -> None:
        self.is_open = True

    def close(self) -> None:
        self.is_open = False


@contextmanager
def managed_resource(name: str, log_list: list[str]) -> Iterator[MockResource]:
    """Generator-based context manager using @contextlib.contextmanager.

    - Logs f"OPEN: {name}" upon entry
    - Yields the MockResource instance
    - Logs f"CLOSE: {name}" upon exit (guaranteed in finally block)
    - If exception occurs inside the with block, logs f"ERROR in {name}: {err}" and re-raises.
    """
    # TODO: try-except-finally 구조로 리소스 생명주기를 안전하게 관리하세요.
    raise NotImplementedError


class DynamicResourceStack:
    """Manages an arbitrary, dynamic number of context managers using ExitStack.

    Guarantees LIFO (Last-In-First-Out) clean up even if opening subsequent resources fails.
    """

    def __init__(self) -> None:
        self._stack = ExitStack()
        self.opened_resources: list[Any] = []

    def __enter__(self) -> "DynamicResourceStack":
        # TODO: self._stack.__enter__()를 호출하고 self를 반환하세요.
        raise NotImplementedError

    def enter_context(self, cm: Any) -> Any:
        """Register and enter a context manager dynamically."""
        # TODO: self._stack.enter_context(cm)을 호출하여 리소스를 획득하고 opened_resources에 추가한 뒤 반환하세요.
        raise NotImplementedError

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        # TODO: self._stack.__exit__을 호출하여 등록된 모든 리소스를 안전하게 닫으세요.
        raise NotImplementedError
