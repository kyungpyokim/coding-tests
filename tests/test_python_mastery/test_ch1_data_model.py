import math

import pytest

from python_mastery.chapter1_data_model import DynamicRecord, Vector


class TestVector:
    def test_initialization_and_len(self):
        v = Vector(1, 2, 3)
        assert len(v) == 3
        assert v.components == (1.0, 2.0, 3.0)

        with pytest.raises(ValueError, match="at least one"):
            Vector()

    def test_indexing_and_slicing(self):
        v = Vector(10, 20, 30, 40)
        assert v[0] == 10.0
        assert v[-1] == 40.0

        sliced = v[1:3]
        assert isinstance(sliced, Vector)
        assert sliced.components == (20.0, 30.0)

    def test_iteration_and_contains(self):
        v = Vector(3, 4, 5)
        assert list(v) == [3.0, 4.0, 5.0]
        assert 4.0 in v
        assert 99.0 not in v

    def test_magnitude_and_bool(self):
        v = Vector(3, 4)
        assert math.isclose(abs(v), 5.0)
        assert bool(v) is True

        zero = Vector(0, 0, 0)
        assert abs(zero) == 0.0
        assert bool(zero) is False

    def test_arithmetic_operations(self):
        v1 = Vector(1, 2, 3)
        v2 = Vector(4, 5, 6)

        # Addition
        v_add = v1 + v2
        assert v_add == Vector(5, 7, 9)

        # Subtraction
        v_sub = v2 - v1
        assert v_sub == Vector(3, 3, 3)

        # Negation
        assert -v1 == Vector(-1, -2, -3)

        # Scalar multiplication
        assert v1 * 2 == Vector(2, 4, 6)
        assert 3 * v1 == Vector(3, 6, 9)

        # Dot product
        assert (v1 @ v2) == 1 * 4 + 2 * 5 + 3 * 6

        # Dimension mismatch
        with pytest.raises(ValueError, match="Dimensions must match"):
            _ = v1 + Vector(1, 2)

    def test_equality_and_hashing(self):
        v1 = Vector(1, 2, 3)
        v2 = Vector(1.0, 2.0, 3.0)
        v3 = Vector(1, 2, 4)

        assert v1 == v2
        assert v1 != v3
        assert hash(v1) == hash(v2)

        # Can be used in sets and dict keys
        s = {v1, v2, v3}
        assert len(s) == 2

        mapping = {v1: "alpha", v3: "beta"}
        assert mapping[v2] == "alpha"

    def test_repr(self):
        v = Vector(1.5, 2.5)
        assert repr(v) == "Vector(1.5, 2.5)"


class TestDynamicRecord:
    def test_dot_and_dict_access(self):
        rec = DynamicRecord({"name": "Alice", "age": 30})

        # Dot access
        assert rec.name == "Alice"
        assert rec.age == 30

        # Dict access
        assert rec["name"] == "Alice"
        assert rec["age"] == 30

        # Membership & len
        assert "name" in rec
        assert len(rec) == 2
        assert set(rec) == {"name", "age"}

    def test_nested_records(self):
        data = {
            "user": {
                "profile": {"city": "Seoul", "score": 95},
                "tags": ["python", "ai"],
            }
        }
        rec = DynamicRecord(data)
        assert isinstance(rec.user, DynamicRecord)
        assert isinstance(rec.user.profile, DynamicRecord)
        assert rec.user.profile.city == "Seoul"
        assert rec["user"]["profile"]["score"] == 95

    def test_mutation_via_dot_and_dict(self):
        rec = DynamicRecord()
        rec.title = "Engineer"
        rec["level"] = 5

        assert rec.title == "Engineer"
        assert rec["level"] == 5

        # Setting nested dict
        rec.settings = {"theme": "dark"}
        assert isinstance(rec.settings, DynamicRecord)
        assert rec.settings.theme == "dark"

    def test_deletion(self):
        rec = DynamicRecord(a=1, b=2, c=3)
        del rec.a
        assert "a" not in rec
        with pytest.raises(AttributeError):
            _ = rec.a

        del rec["b"]
        assert "b" not in rec
        with pytest.raises(KeyError):
            _ = rec["b"]

    def test_to_dict_export(self):
        orig = {"a": 1, "nested": {"b": 2, "c": 3}}
        rec = DynamicRecord(orig)
        exported = rec.to_dict()
        assert exported == orig
        assert type(exported) is dict
        assert type(exported["nested"]) is dict
