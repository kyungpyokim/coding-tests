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
    res = MockResource(name)
    res.open()
    log_list.append(f"OPEN: {name}")
    try:
        yield res
    except Exception as e:
        log_list.append(f"ERROR in {name}: {e}")
        raise
    finally:
        res.close()
        log_list.append(f"CLOSE: {name}")


class DynamicResourceStack:
    def __init__(self) -> None:
        self._stack = ExitStack()
        self.opened_resources: list[Any] = []

    def __enter__(self) -> "DynamicResourceStack":
        self._stack.__enter__()
        return self

    def enter_context(self, cm: Any) -> Any:
        res = self._stack.enter_context(cm)
        self.opened_resources.append(res)
        return res

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        return bool(self._stack.__exit__(exc_type, exc_val, exc_tb))
