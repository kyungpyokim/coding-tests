import math
from collections.abc import Iterator
from typing import Any, Union


class Vector:
    """An immutable, multi-dimensional Euclidean vector."""

    def __init__(self, *components: float) -> None:
        if not components:
            raise ValueError("Vector must have at least one component")
        self._components = tuple(float(c) for c in components)

    @property
    def components(self) -> tuple[float, ...]:
        return self._components

    def __len__(self) -> int:
        return len(self._components)

    def __getitem__(self, index: int | slice) -> Union[float, "Vector"]:
        if isinstance(index, slice):
            return Vector(*self._components[index])
        return self._components[index]

    def __iter__(self) -> Iterator[float]:
        return iter(self._components)

    def __contains__(self, value: Any) -> bool:
        return value in self._components

    def __abs__(self) -> float:
        return math.sqrt(sum(c**2 for c in self._components))

    def __bool__(self) -> bool:
        return bool(abs(self) != 0.0)

    def __neg__(self) -> "Vector":
        return Vector(*(-c for c in self._components))

    def __add__(self, other: "Vector") -> "Vector":
        if not isinstance(other, Vector):
            return NotImplemented
        if len(self) != len(other):
            raise ValueError(f"Dimensions must match: {len(self)} != {len(other)}")
        return Vector(
            *(a + b for a, b in zip(self._components, other._components, strict=True))
        )

    def __sub__(self, other: "Vector") -> "Vector":
        if not isinstance(other, Vector):
            return NotImplemented
        if len(self) != len(other):
            raise ValueError(f"Dimensions must match: {len(self)} != {len(other)}")
        return Vector(
            *(a - b for a, b in zip(self._components, other._components, strict=True))
        )

    def __mul__(self, scalar: int | float) -> "Vector":
        if not isinstance(scalar, (int, float)):
            return NotImplemented
        return Vector(*(c * scalar for c in self._components))

    def __rmul__(self, scalar: int | float) -> "Vector":
        return self.__mul__(scalar)

    def __matmul__(self, other: "Vector") -> float:
        if not isinstance(other, Vector):
            return NotImplemented
        if len(self) != len(other):
            raise ValueError(f"Dimensions must match: {len(self)} != {len(other)}")
        return sum(
            a * b for a, b in zip(self._components, other._components, strict=True)
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Vector):
            return NotImplemented
        return self._components == other._components

    def __hash__(self) -> int:
        return hash(self._components)

    def __repr__(self) -> str:
        formatted = ", ".join(str(c) for c in self._components)
        return f"Vector({formatted})"
