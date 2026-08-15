from typing import Any


class AtomicTransaction:
    """Context Manager implementing atomic dictionary state transactions.

    Demonstrates Low-Level Context Manager Protocol:
    - __enter__(self): Takes snapshot of dict_store and returns mutable working proxy
    - __exit__(self, exc_type, exc_val, exc_tb):
        * If no exception: Commits changes to target store.
        * If exception occurred: Rolls back (discards changes) without mutating original.
        * If suppress_exceptions is True: Returns True to suppress specified exception types.
    """

    def __init__(
        self,
        store: dict[str, Any],
        suppress_exceptions: tuple[type[Exception], ...] | None = None,
    ) -> None:
        self.store = store
        self.suppress_exceptions = suppress_exceptions or ()
        self._working_copy: dict[str, Any] = {}

    def __enter__(self) -> dict[str, Any]:
        # TODO: store의 딥카피(_working_copy)를 생성하고 반환하세요.
        raise NotImplementedError

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any,
    ) -> bool:
        # TODO: exc_type이 None이면 self._working_copy의 내용을 self.store에 커밋(갱신 및 삭제 반영)하세요.
        # exc_type이 존재하고 self.suppress_exceptions에 해당하는 경우 True를 반환해 예외를 억제하세요.
        # 그 외의 경우 False를 반환하여 예외를 전파하세요.
        raise NotImplementedError
