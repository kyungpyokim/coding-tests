from functools import singledispatch, singledispatchmethod
from typing import Any


@singledispatch
def serialize(obj: Any) -> Any:
    """Generic polymorphic serializer using functools.singledispatch.

    Default: Returns str(obj) or raises TypeError if unhandled.
    Dispatches:
    - int, float, bool, str: identity (returns as-is)
    - list, tuple, set: list of serialized elements
    - dict: dict with string keys and serialized values
    - datetime, date: ISO-8601 formatted string (.isoformat())
    - dataclass instances: dict via asdict and serialized
    """
    # TODO: 기본 디스패치 핸들러 및 각 타입별 @serialize.register 핸들러들을 구현하세요.
    raise NotImplementedError


class DataPipeline:
    """Demonstrates singledispatchmethod inside a class context."""

    def __init__(self, prefix: str = "PROCESSED") -> None:
        self.prefix = prefix

    @singledispatchmethod
    def process(self, data: Any) -> str:
        """Default fallback for unsupported data types."""
        # TODO: 기본 핸들러를 정의하세요. (f"[{self.prefix}] UNKNOWN: {data}")
        raise NotImplementedError

    # TODO: @process.register를 이용해 str, int, list 에 대한 메서드 오버로드를 작성하세요.
