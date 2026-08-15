import re
from abc import ABC, abstractmethod
from typing import Any


class Validator(ABC):
    """Abstract Base Descriptor for attribute validation.

    Demonstrates Descriptor Protocol:
    - __set_name__(self, owner, name): Captures attribute name automatically (Python 3.6+)
    - __get__(self, instance, owner): Retrieves value from instance.__dict__
    - __set__(self, instance, value): Validates and stores value into instance.__dict__
    """

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        # TODO: instance가 None(클래스에서 접근 시)이면 self를 반환하고,
        # 인스턴스에서 접근 시 instance.__dict__에서 값을 조회하세요. 없으면 None 또는 기본값 반환.
        raise NotImplementedError

    def __set__(self, instance: Any, value: Any) -> None:
        # TODO: validate(value)를 호출하여 검증하고 instance.__dict__[self.private_name]에 저장하세요.
        raise NotImplementedError

    @abstractmethod
    def validate(self, value: Any) -> Any:
        """Subclasses must implement validation logic."""


class Typed(Validator):
    """Descriptor enforcing specific type."""

    def __init__(self, expected_type: type | tuple[type, ...]) -> None:
        self.expected_type = expected_type

    def validate(self, value: Any) -> Any:
        # TODO: value가 expected_type의 인스턴스가 아니면 TypeError를 발생시키세요.
        raise NotImplementedError


class BoundedNumber(Validator):
    """Descriptor enforcing numeric bounds [min_val, max_val]."""

    def __init__(
        self,
        min_val: float | None = None,
        max_val: float | None = None,
    ) -> None:
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, value: Any) -> Any:
        # TODO: value가 int/float인지 확인하고(아니면 TypeError),
        # min_val/max_val 범위를 벗어나면 ValueError를 발생시키세요.
        raise NotImplementedError


class RegexString(Validator):
    """Descriptor enforcing regex string format."""

    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        self._regex = re.compile(pattern)

    def validate(self, value: Any) -> str:
        # TODO: value가 str이 아니면 TypeError,
        # 정규식 패턴과 매칭되지 않으면 ValueError를 발생시키세요.
        raise NotImplementedError


class UserSchema:
    """Schema example utilizing custom descriptors."""

    username = RegexString(r"^[a-zA-Z0-9_]{3,16}$")
    age = BoundedNumber(min_val=0, max_val=150)
    email = RegexString(r"^[\w\.-]+@[\w\.-]+\.\w+$")

    def __init__(self, username: str, age: int, email: str) -> None:
        self.username = username
        self.age = age
        self.email = email
