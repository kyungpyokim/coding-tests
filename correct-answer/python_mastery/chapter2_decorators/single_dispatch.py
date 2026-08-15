from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from functools import singledispatch, singledispatchmethod
from typing import Any


@singledispatch
def serialize(obj: Any) -> Any:
    if is_dataclass(obj) and not isinstance(obj, type):
        return serialize(asdict(obj))
    return str(obj)


@serialize.register(int)
@serialize.register(float)
@serialize.register(bool)
@serialize.register(str)
def _serialize_primitive(obj: int | float | bool | str) -> int | float | bool | str:
    return obj


@serialize.register(list)
@serialize.register(tuple)
@serialize.register(set)
def _serialize_sequence(obj: list[Any] | tuple[Any, ...] | set[Any]) -> list[Any]:
    return [serialize(item) for item in obj]


@serialize.register(dict)
def _serialize_dict(obj: dict[Any, Any]) -> dict[str, Any]:
    return {str(k): serialize(v) for k, v in obj.items()}


@serialize.register(datetime)
@serialize.register(date)
def _serialize_datetime(obj: datetime | date) -> str:
    return obj.isoformat()


class DataPipeline:
    def __init__(self, prefix: str = "PROCESSED") -> None:
        self.prefix = prefix

    @singledispatchmethod
    def process(self, data: Any) -> str:
        return f"[{self.prefix}] UNKNOWN: {data!r}"

    @process.register(str)
    def _process_str(self, data: str) -> str:
        return f"[{self.prefix}] TEXT({len(data)}): {data.upper()}"

    @process.register(int)
    @process.register(float)
    def _process_num(self, data: int | float) -> str:
        return f"[{self.prefix}] NUM: {data * 2}"

    @process.register(list)
    def _process_list(self, data: list[Any]) -> str:
        items_str = ", ".join(str(x) for x in data)
        return f"[{self.prefix}] BATCH({len(data)}): [{items_str}]"
