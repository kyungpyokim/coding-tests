from typing import Any, ClassVar


class BasePlugin:
    """Plugin architecture using __init_subclass__."""

    _registry: ClassVar[dict[str, type["BasePlugin"]]] = {}
    plugin_name: ClassVar[str] = ""

    def __init_subclass__(cls, plugin_name: str | None = None, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        name = plugin_name or getattr(cls, "plugin_name", "")
        if not name:
            raise ValueError(
                f"Plugin class {cls.__name__} must define a non-empty plugin_name"
            )
        if name in cls._registry:
            raise KeyError(f"Plugin with name '{name}' already registered")
        cls.plugin_name = name
        cls._registry[name] = cls

    @classmethod
    def get_plugin(cls, name: str) -> type["BasePlugin"]:
        if name not in cls._registry:
            raise KeyError(f"No plugin found with name '{name}'")
        return cls._registry[name]


class StrictSchemaMeta(type):
    """Metaclass that validates class definitions at creation time."""

    def __new__(
        mcs,
        name: str,
        bases: tuple[type, ...],
        namespace: dict[str, Any],
        **kwargs: Any,
    ) -> type:
        # Check forbidden methods
        for attr_name in namespace:
            if attr_name.startswith("danger_"):
                raise TypeError(
                    f"Forbidden method name '{attr_name}' in class '{name}'"
                )

        annotations = namespace.get("__annotations__", {})
        # Verify non-dunder non-private attributes have annotations or are callables
        for key, val in namespace.items():
            if (
                not key.startswith("_")
                and not callable(val)
                and not isinstance(val, (property, classmethod, staticmethod))
                and key not in annotations
            ):
                raise TypeError(
                    f"Attribute '{key}' in '{name}' must have a type annotation"
                )

        namespace["__fields__"] = tuple(annotations.keys())
        return super().__new__(mcs, name, bases, namespace)
