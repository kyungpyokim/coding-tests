import weakref
from typing import Any, Generic, TypeVar

T = TypeVar("T")


class OptimizedNode:
    """Memory-optimized node using __slots__.

    Features:
    - Defines `__slots__ = ("name", "value", "_parent", "__weakref__")`.
    - Eliminates `__dict__` overhead on instances.
    - Prevents arbitrary attribute assignment outside slots.
    - Supports weak references via `__weakref__`.
    """

    __slots__ = ("_parent", "__weakref__", "name", "value")

    def __init__(
        self, name: str, value: Any, parent: "OptimizedNode | None" = None
    ) -> None:
        self.name = name
        self.value = value
        # Use weak reference for parent to avoid cyclic reference leaks
        self._parent = weakref.ref(parent) if parent is not None else None

    @property
    def parent(self) -> "OptimizedNode | None":
        """Return dereferenced parent node or None."""
        # TODO: self._parent가 None이 아니면 역참조(() 호출)하여 반환하세요.
        raise NotImplementedError


class WeakRefCache(Generic[T]):
    """In-memory cache using WeakValueDictionary to prevent memory leaks.

    When cached values are garbage collected elsewhere, they automatically disappear from cache.
    """

    def __init__(self) -> None:
        # TODO: weakref.WeakValueDictionary를 초기화하세요.
        raise NotImplementedError

    def set(self, key: str, value: Any) -> None:
        """Store value in cache."""
        # TODO: key와 value를 저장하세요.
        raise NotImplementedError

    def get(self, key: str) -> Any:
        """Retrieve value by key or return None."""
        # TODO: key에 해당하는 값을 반환하거나 없으면 None을 반환하세요.
        raise NotImplementedError

    def __len__(self) -> int:
        """Return number of currently alive cached objects."""
        # TODO: 캐시에 남아있는 객체 수를 반환하세요.
        raise NotImplementedError
