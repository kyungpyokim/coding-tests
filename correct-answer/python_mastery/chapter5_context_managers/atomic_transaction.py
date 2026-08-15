import copy
from typing import Any


class AtomicTransaction:
    def __init__(
        self,
        store: dict[str, Any],
        suppress_exceptions: tuple[type[Exception], ...] | None = None,
    ) -> None:
        self.store = store
        self.suppress_exceptions = suppress_exceptions or ()
        self._working_copy: dict[str, Any] = {}

    def __enter__(self) -> dict[str, Any]:
        self._working_copy = copy.deepcopy(self.store)
        return self._working_copy

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        if exc_type is None:
            # Commit changes
            self.store.clear()
            self.store.update(self._working_copy)
            return False

        # Rollback is automatic since store was untouched.
        # Check suppression
        return bool(
            issubclass(exc_type, Exception)
            and issubclass(exc_type, self.suppress_exceptions)
        )
