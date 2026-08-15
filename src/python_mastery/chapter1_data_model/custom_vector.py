from collections.abc import Iterator
from typing import Any, Union


class Vector:
    """An immutable, multi-dimensional Euclidean vector.

    Demonstrates Python's Data Model:
    - Sequence Protocol: __len__, __getitem__, __iter__, __contains__
    - Operator Overloading: __add__, __sub__, __mul__, __matmul__, __neg__, __abs__
    - Object Representation: __repr__, __str__
    - Hashing & Equality: __eq__, __hash__ (enables use in sets and dict keys)
    - Boolean conversion: __bool__
    """

    def __init__(self, *components: float) -> None:
        """Initialize vector with float/int components.

        Raises:
            ValueError: If no components are provided.
        """
        # TODO: components가 비어있으면 ValueError를 발생시키고,
        # 요소들을 float 튜플로 변환하여 내부 `_components`에 저장하세요.
        raise NotImplementedError

    @property
    def components(self) -> tuple[float, ...]:
        """Return the vector components as a tuple."""
        # TODO: 내부 _components 튜플을 반환하세요.
        raise NotImplementedError

    def __len__(self) -> int:
        """Return the number of dimensions/components."""
        # TODO: 차원 수를 반환하세요.
        raise NotImplementedError

    def __getitem__(self, index: int | slice) -> Union[float, "Vector"]:
        """Support indexing and slicing.

        Indexing (e.g. v[0]) returns a float.
        Slicing (e.g. v[1:3]) returns a new Vector instance.
        """
        # TODO: index가 slice인 경우 새 Vector 인스턴스를 반환하고,
        # int인 경우 해당 float 값을 반환하세요.
        raise NotImplementedError

    def __iter__(self) -> Iterator[float]:
        """Support iteration over components."""
        # TODO: 내부 컴포넌트들의 이터레이터를 반환하세요.
        raise NotImplementedError

    def __contains__(self, value: Any) -> bool:
        """Support the `in` operator."""
        # TODO: value가 components에 존재하는지 확인하세요.
        raise NotImplementedError

    def __abs__(self) -> float:
        """Return the Euclidean norm (magnitude) of the vector: sqrt(sum(x^2))."""
        # TODO: 유클리드 노름(크기)을 계산하여 반환하세요.
        raise NotImplementedError

    def __bool__(self) -> bool:
        """Return True if magnitude is non-zero, False otherwise."""
        # TODO: 벡터의 크기가 0이 아니면 True를 반환하세요.
        raise NotImplementedError

    def __neg__(self) -> "Vector":
        """Return the negation of the vector (-v)."""
        # TODO: 모든 컴포넌트의 부호가 반전된 새 Vector를 반환하세요.
        raise NotImplementedError

    def __add__(self, other: "Vector") -> "Vector":
        """Add two vectors element-wise.

        Raises:
            TypeError: If other is not a Vector.
            ValueError: If vectors have different dimensions.
        """
        # TODO: 다른 Vector와 요소별 덧셈을 수행한 새 Vector를 반환하세요.
        raise NotImplementedError

    def __sub__(self, other: "Vector") -> "Vector":
        """Subtract another vector element-wise.

        Raises:
            TypeError: If other is not a Vector.
            ValueError: If vectors have different dimensions.
        """
        # TODO: 다른 Vector와의 요소별 뺄셈을 수행한 새 Vector를 반환하세요.
        raise NotImplementedError

    def __mul__(self, scalar: int | float) -> "Vector":
        """Scalar multiplication: v * scalar."""
        # TODO: 스칼라와의 곱셈을 수행한 새 Vector를 반환하세요.
        # scalar가 int/float가 아니면 TypeError를 발생시키세요.
        raise NotImplementedError

    def __rmul__(self, scalar: int | float) -> "Vector":
        """Reflected scalar multiplication: scalar * v."""
        # TODO: __mul__을 호출하여 스칼라 곱을 지원하세요.
        raise NotImplementedError

    def __matmul__(self, other: "Vector") -> float:
        """Dot product (inner product): v @ other.

        Raises:
            TypeError: If other is not a Vector.
            ValueError: If vectors have different dimensions.
        """
        # TODO: 두 벡터 간의 내적(dot product, sum(a * b))을 계산하여 반환하세요.
        raise NotImplementedError

    def __eq__(self, other: Any) -> bool:
        """Vectors are equal if all components match exactly."""
        # TODO: other가 Vector이고 components가 일치하는지 비교하세요.
        raise NotImplementedError

    def __hash__(self) -> int:
        """Compute hash based on components so Vector can be a dict key or set member."""
        # TODO: components 튜플의 해시값을 반환하세요.
        raise NotImplementedError

    def __repr__(self) -> str:
        """Return developer-friendly string: Vector(1.0, 2.0, 3.0)."""
        # TODO: Vector(x, y, ...) 형태의 문자열을 반환하세요.
        raise NotImplementedError
