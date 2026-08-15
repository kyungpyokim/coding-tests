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
    try:
        return func()
    except InternalDatabaseError as err:
        if hide_internal_details:
            raise PublicAPIError("Request processing failed") from None
        else:
            raise ApplicationError("Database transaction failed") from err


@dataclass
class ExecutionSummary:
    successes: list[Any]
    errors: list[Exception]


class MultiTaskRunner:
    def __init__(self, group_message: str = "Multiple task failures occurred") -> None:
        self.group_message = group_message

    def run_all(self, tasks: list[Callable[[], Any]]) -> ExecutionSummary:
        successes: list[Any] = []
        errors: list[Exception] = []

        for task in tasks:
            try:
                successes.append(task())
            except Exception as e:
                errors.append(e)

        if errors:
            raise ExceptionGroup(self.group_message, errors)

        return ExecutionSummary(successes=successes, errors=[])
