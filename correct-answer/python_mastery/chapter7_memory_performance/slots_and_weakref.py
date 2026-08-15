import weakref
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class OptimizedNode:
    __slots__ = ("_parent", "__weakref__", "name", "value")

    def __init__(
        self, name: str, value: Any, parent: "OptimizedNode | None" = None
    ) -> None:
        self.name = name
        self.value = value
        self._parent = weakref.ref(parent) if parent is not None else None

    @property
    def parent(self) -> "OptimizedNode | None":
        return self._parent() if self._parent is not None else None


class WeakRefCache(Generic[T]):
    def __init__(self) -> None:
        self._cache: weakref.WeakValueDictionary[str, Any] = (
            weakref.WeakValueDictionary()
        )

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def get(self, key: str) -> Any:
        return self._cache.get(key, None)

    def __len__(self) -> int:
        return len(self._cache)
