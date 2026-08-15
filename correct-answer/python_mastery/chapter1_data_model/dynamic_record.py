from collections.abc import Iterator, Mapping
from typing import Any


class DynamicRecord:
    """A hybrid record supporting both attribute (dot) and mapping (dict) access."""

    def __init__(self, data: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        object.__setattr__(self, "_data", {})
        combined: dict[str, Any] = {}
        if data is not None:
            combined.update(data)
        combined.update(kwargs)

        for k, v in combined.items():
            self[k] = v

    def __getattr__(self, name: str) -> Any:
        data = object.__getattribute__(self, "_data")
        if name in data:
            return data[name]
        raise AttributeError(
            f"'{type(self).__name__}' object has no attribute '{name}'"
        )

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            object.__setattr__(self, name, value)
        else:
            self[name] = value

    def __delattr__(self, name: str) -> None:
        data = object.__getattribute__(self, "_data")
        if name in data:
            del data[name]
        else:
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def __setitem__(self, key: str, value: Any) -> None:
        if isinstance(value, Mapping) and not isinstance(value, DynamicRecord):
            self._data[key] = DynamicRecord(value)
        else:
            self._data[key] = value

    def __delitem__(self, key: str) -> None:
        del self._data[key]

    def __contains__(self, key: Any) -> bool:
        return key in self._data

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Iterator[str]:
        return iter(self._data)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for k, v in self._data.items():
            if isinstance(v, DynamicRecord):
                result[k] = v.to_dict()
            elif isinstance(v, list):
                result[k] = [
                    item.to_dict() if isinstance(item, DynamicRecord) else item
                    for item in v
                ]
            else:
                result[k] = v
        return result

    def __repr__(self) -> str:
        return f"DynamicRecord({self._data!r})"
