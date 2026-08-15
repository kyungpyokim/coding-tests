import pytest

from python_mastery.chapter3_descriptors import (
    BasePlugin,
    BoundedNumber,
    RegexString,
    StrictSchemaMeta,
    Typed,
    UserSchema,
)


class TestValidators:
    def test_typed_validator(self):
        class Model:
            age = Typed(int)

        m = Model()
        m.age = 25
        assert m.age == 25

        with pytest.raises(TypeError, match="Expected int"):
            m.age = "twenty-five"

    def test_bounded_number_validator(self):
        class Product:
            price = BoundedNumber(min_val=0.0, max_val=1000.0)

        p = Product()
        p.price = 99.9
        assert p.price == 99.9

        with pytest.raises(ValueError, match="less than min"):
            p.price = -1.0

        with pytest.raises(ValueError, match="greater than max"):
            p.price = 1500.0

    def test_regex_string_validator(self):
        class Account:
            code = RegexString(r"^[A-Z]{3}-\d{4}$")

        acc = Account()
        acc.code = "ABC-1234"
        assert acc.code == "ABC-1234"

        with pytest.raises(ValueError, match="does not match pattern"):
            acc.code = "invalid-code"

    def test_user_schema_integration(self):
        user = UserSchema(username="alice_dev", age=28, email="alice@example.com")
        assert user.username == "alice_dev"
        assert user.age == 28
        assert user.email == "alice@example.com"

        with pytest.raises(ValueError):
            user.age = 200

        with pytest.raises(ValueError):
            user.email = "not-an-email"


class TestPluginRegistry:
    def test_auto_registration(self):
        class AuthPlugin(BasePlugin, plugin_name="auth"):
            pass

        class LoggerPlugin(BasePlugin):
            plugin_name = "logger"

        assert BasePlugin.get_plugin("auth") is AuthPlugin
        assert BasePlugin.get_plugin("logger") is LoggerPlugin

        with pytest.raises(KeyError, match="already registered"):

            class DuplicateAuth(BasePlugin, plugin_name="auth"):
                pass

        with pytest.raises(KeyError, match="No plugin found"):
            BasePlugin.get_plugin("unknown")

        with pytest.raises(ValueError, match="must define a non-empty plugin_name"):

            class AnonymousPlugin(BasePlugin):
                pass


class TestStrictSchemaMeta:
    def test_valid_schema_creation(self):
        class User(metaclass=StrictSchemaMeta):
            name: str
            age: int = 0

            def greet(self) -> str:
                return f"Hello {self.name}"

        assert User.__fields__ == ("name", "age")
        u = User()
        u.name = "Bob"
        assert u.greet() == "Hello Bob"

    def test_forbidden_method_raises(self):
        with pytest.raises(TypeError, match="Forbidden method name"):

            class BadClass(metaclass=StrictSchemaMeta):
                def danger_eval(self):
                    pass

    def test_unannotated_attribute_raises(self):
        with pytest.raises(TypeError, match="must have a type annotation"):

            class UnannotatedClass(metaclass=StrictSchemaMeta):
                untyped_field = 123
