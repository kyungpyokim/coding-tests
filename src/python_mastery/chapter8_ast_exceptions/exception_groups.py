from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeVar

T = TypeVar("T")


class ApplicationError(Exception):
    """Domain base exception."""


class InternalDatabaseError(Exception):
    """Low-level database driver exception."""


class PublicAPIError(Exception):
    """Sanitized public exception."""


def safe_execute_with_chaining(
    func: Callable[[], T],
    hide_internal_details: bool = False,
) -> T:
    """Demonstrates Python's Exception Chaining (`from e` vs `from None`).

    - Executes `func()`.
    - If `InternalDatabaseError` is raised:
        * If `hide_internal_details` is True:
          raises `PublicAPIError("Request processing failed") from None` (suppresses __cause__ and __context__).
        * If `hide_internal_details` is False:
          raises `ApplicationError("Database transaction failed") from err` (preserves __cause__).
    """
    # TODO: try-except 블록으로 위 요구사항에 맞게 예외를 체이닝하여 발생시키세요.
    raise NotImplementedError


@dataclass
class ExecutionSummary:
    successes: list[Any]
    errors: list[Exception]


class MultiTaskRunner:
    """Executes multiple tasks and aggregates errors using Python 3.11+ ExceptionGroup."""

    def __init__(self, group_message: str = "Multiple task failures occurred") -> None:
        self.group_message = group_message

    def run_all(self, tasks: list[Callable[[], Any]]) -> ExecutionSummary:
        """Run all tasks sequentially, collecting return values and exceptions.

        Raises:
            ExceptionGroup: If any tasks failed, containing all collected exceptions.
        """
        # TODO: 모든 tasks를 실행하여 성공한 결과는 successes에, 실패한 예외는 errors에 수집하세요.
        # errors가 비어있지 않다면 ExceptionGroup(self.group_message, errors)을 raise 하세요.
        # 모두 성공했다면 ExecutionSummary(successes, [])를 반환하세요.
        raise NotImplementedError
