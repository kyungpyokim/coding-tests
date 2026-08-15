import pytest

from python_mastery.chapter5_context_managers import (
    AtomicTransaction,
    DynamicResourceStack,
    managed_resource,
)


class TestAtomicTransaction:
    def test_successful_transaction_commits(self):
        store = {"balance": 100, "user": "Alice"}
        with AtomicTransaction(store) as tx:
            tx["balance"] += 50
            tx["status"] = "VIP"

        assert store == {"balance": 150, "user": "Alice", "status": "VIP"}

    def test_failed_transaction_rolls_back(self):
        store = {"balance": 100, "user": "Alice"}
        with (
            pytest.raises(ValueError, match="Operation failed"),
            AtomicTransaction(store) as tx,
        ):
            tx["balance"] += 50
            raise ValueError("Operation failed")

        # Must remain untouched
        assert store == {"balance": 100, "user": "Alice"}

    def test_exception_suppression(self):
        store = {"count": 10}
        with AtomicTransaction(store, suppress_exceptions=(KeyError,)) as tx:
            tx["count"] = 99
            raise KeyError("Suppressed error")

        # Rollback happened and exception was suppressed
        assert store == {"count": 10}


class TestResourcePool:
    def test_managed_resource_lifecycle(self):
        logs = []
        with managed_resource("DB_CONN", logs) as res:
            assert res.is_open is True
            assert logs == ["OPEN: DB_CONN"]

        assert res.is_open is False
        assert logs == ["OPEN: DB_CONN", "CLOSE: DB_CONN"]

    def test_managed_resource_on_error(self):
        logs = []
        with pytest.raises(RuntimeError), managed_resource("FILE_HANDLE", logs):
            raise RuntimeError("Disk full")

        assert logs == [
            "OPEN: FILE_HANDLE",
            "ERROR in FILE_HANDLE: Disk full",
            "CLOSE: FILE_HANDLE",
        ]

    def test_dynamic_resource_stack(self):
        logs = []
        with DynamicResourceStack() as stack:
            stack.enter_context(managed_resource("R1", logs))
            stack.enter_context(managed_resource("R2", logs))
            assert len(stack.opened_resources) == 2

        # Verify LIFO close order
        assert logs == ["OPEN: R1", "OPEN: R2", "CLOSE: R2", "CLOSE: R1"]
