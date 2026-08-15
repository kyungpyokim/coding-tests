import re
from abc import ABC, abstractmethod
from typing import Any


class Validator(ABC):
    """Abstract Base Descriptor for attribute validation."""

    def __set_name__(self, owner: type, name: str) -> None:
        self.public_name = name
        self.private_name = f"_{name}"

    def __get__(self, instance: Any, owner: type | None = None) -> Any:
        if instance is None:
            return self
        return instance.__dict__.get(self.private_name, None)

    def __set__(self, instance: Any, value: Any) -> None:
        validated_value = self.validate(value)
        instance.__dict__[self.private_name] = validated_value

    @abstractmethod
    def validate(self, value: Any) -> Any:
        """Subclasses must implement validation logic."""


class Typed(Validator):
    def __init__(self, expected_type: type | tuple[type, ...]) -> None:
        self.expected_type = expected_type

    def validate(self, value: Any) -> Any:
        if not isinstance(value, self.expected_type):
            expected_name = (
                tuple(t.__name__ for t in self.expected_type)
                if isinstance(self.expected_type, tuple)
                else self.expected_type.__name__
            )
            raise TypeError(f"Expected {expected_name}, got {type(value).__name__}")
        return value


class BoundedNumber(Validator):
    def __init__(
        self,
        min_val: float | None = None,
        max_val: float | None = None,
    ) -> None:
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, value: Any) -> Any:
        if not isinstance(value, (int, float)):
            raise TypeError(f"Expected number, got {type(value).__name__}")
        if self.min_val is not None and value < self.min_val:
            raise ValueError(f"Value {value} is less than min {self.min_val}")
        if self.max_val is not None and value > self.max_val:
            raise ValueError(f"Value {value} is greater than max {self.max_val}")
        return value


class RegexString(Validator):
    def __init__(self, pattern: str) -> None:
        self.pattern = pattern
        self._regex = re.compile(pattern)

    def validate(self, value: Any) -> str:
        if not isinstance(value, str):
            raise TypeError(f"Expected str, got {type(value).__name__}")
        if not self._regex.match(value):
            raise ValueError(
                f"String '{value}' does not match pattern '{self.pattern}'"
            )
        return value


class UserSchema:
    username = RegexString(r"^[a-zA-Z0-9_]{3,16}$")
    age = BoundedNumber(min_val=0, max_val=150)
    email = RegexString(r"^[\w\.-]+@[\w\.-]+\.\w+$")

    def __init__(self, username: str, age: int, email: str) -> None:
        self.username = username
        self.age = age
        self.email = email
