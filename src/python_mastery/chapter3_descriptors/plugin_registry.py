from typing import Any, ClassVar


class BasePlugin:
    """Plugin architecture using __init_subclass__ (Modern Metaprogramming).

    Features:
    - Automatically registers subclasses into a class-level `_registry` dict.
    - Requires each subclass to define a non-empty `plugin_name` class attribute
      or pass `plugin_name="xyz"` as a keyword argument in class definition.
    - Provides `get_plugin(name)` class method to retrieve registered plugin classes.
    """

    _registry: ClassVar[dict[str, type["BasePlugin"]]] = {}
    plugin_name: ClassVar[str] = ""

    def __init_subclass__(cls, plugin_name: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        # TODO: plugin_name 파라미터 또는 cls.plugin_name을 확인하여,
        # 유효한 이름이 없으면 ValueError를 발생시키고,
        # 중복된 이름이 이미 등록되어 있으면 KeyError를 발생시키며,
        # cls._registry[name] = cls 로 등록하세요.
        raise NotImplementedError

    @classmethod
    def get_plugin(cls, name: str) -> type["BasePlugin"]:
        """Retrieve registered plugin class by name."""
        # TODO: cls._registry에서 name을 조회하고 없으면 KeyError를 발생시키세요.
        raise NotImplementedError


class StrictSchemaMeta(type):
    """Metaclass that validates class definitions at import/creation time.

    Features:
    - Enforces that all class attributes without leading underscores have type annotations.
    - Collects all annotated field names into a tuple `__fields__` attached to the class.
    - Forbids any method starting with `danger_`.
    """

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> type:
        # TODO: namespace의 메서드 중 'danger_'로 시작하는 것이 있으면 TypeError를 발생시키세요.
        # annotations = namespace.get("__annotations__", {})
        # 비공개 속성이 아닌 일반 속성에 타입 어노테이션이 누락된 경우 TypeError 발생.
        # namespace["__fields__"] = tuple(annotations.keys())
        # super().__new__(mcs, name, bases, namespace) 호출하여 클래스를 생성하세요.
        raise NotImplementedError
