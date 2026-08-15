import pytest

from python_mastery.chapter8_ast_exceptions import (
    ApplicationError,
    InternalDatabaseError,
    MultiTaskRunner,
    PublicAPIError,
    SecurityScanner,
    safe_execute_with_chaining,
    validate_callable_signature,
)


class TestASTSecurityScanner:
    def test_safe_source_code(self):
        code = """
def calculate_sum(a: int, b: int) -> int:
    result = a + b
    return result
"""
        report = SecurityScanner.scan_source(code)
        assert report.is_safe is True
        assert report.forbidden_calls == []
        assert report.forbidden_attributes == []
        assert report.has_global_statement is False

    def test_dangerous_source_code(self):
        code = """
def dangerous_func(x):
    global bad_state
    eval("print('injected')")
    open('/etc/passwd')
    return x.__class__.__subclasses__()
"""
        report = SecurityScanner.scan_source(code)
        assert report.is_safe is False
        assert "eval" in report.forbidden_calls
        assert "open" in report.forbidden_calls
        assert "__subclasses__" in report.forbidden_attributes
        assert report.has_global_statement is True

    def test_signature_validation(self):
        def valid_handler(req_id: str, timeout: int) -> bool:
            return True

        def missing_param(req_id: str) -> bool:
            return True

        def unannotated(req_id, timeout) -> bool:
            return True

        assert (
            validate_callable_signature(
                valid_handler, ["req_id", "timeout"], require_type_annotations=True
            )
            is True
        )
        assert (
            validate_callable_signature(missing_param, ["req_id", "timeout"]) is False
        )
        assert (
            validate_callable_signature(
                unannotated, ["req_id", "timeout"], require_type_annotations=True
            )
            is False
        )
        assert (
            validate_callable_signature(
                unannotated, ["req_id", "timeout"], require_type_annotations=False
            )
            is True
        )


class TestExceptionChainingAndGroups:
    def test_safe_execute_with_cause_preservation(self):
        def faulty_db():
            raise InternalDatabaseError("Connection timeout on port 5432")

        with pytest.raises(
            ApplicationError, match="Database transaction failed"
        ) as exc_info:
            safe_execute_with_chaining(faulty_db, hide_internal_details=False)

        # __cause__ must be InternalDatabaseError
        assert isinstance(exc_info.value.__cause__, InternalDatabaseError)

    def test_safe_execute_with_details_hidden(self):
        def faulty_db():
            raise InternalDatabaseError("Connection timeout on port 5432")

        with pytest.raises(
            PublicAPIError, match="Request processing failed"
        ) as exc_info:
            safe_execute_with_chaining(faulty_db, hide_internal_details=True)

        # __cause__ must be suppressed (None)
        assert exc_info.value.__cause__ is None
        assert exc_info.value.__suppress_context__ is True

    def test_multi_task_runner_exception_group(self):
        runner = MultiTaskRunner("Batch processing failed")

        tasks = [
            lambda: 10 * 2,
            lambda: int("not_a_number"),
            lambda: [][10],
            lambda: "success",
        ]

        with pytest.raises(ExceptionGroup) as exc_info:
            runner.run_all(tasks)

        eg = exc_info.value
        assert eg.message == "Batch processing failed"
        assert len(eg.exceptions) == 2
        assert any(isinstance(e, ValueError) for e in eg.exceptions)
        assert any(isinstance(e, IndexError) for e in eg.exceptions)
