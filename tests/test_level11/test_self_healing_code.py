import pytest

from ai_practice.level11_evaluator_optimizer.self_healing_code import (
    EvaluationResult,
    SelfHealingWorkflow,
    validate_python_syntax,
)


@pytest.mark.unit
class TestSelfHealingCode:
    def test_validate_python_syntax(self):
        valid_code = "def add(a, b):\n    return a + b\n"
        invalid_code = "def add(a, b)\n    return a + b\n"  # missing colon

        is_valid, err = validate_python_syntax(valid_code)
        assert is_valid is True
        assert err is None

        is_valid_bad, err_bad = validate_python_syntax(invalid_code)
        assert is_valid_bad is False
        assert (
            "invalid syntax" in (err_bad or "").lower()
            or "expected" in (err_bad or "").lower()
        )

    def test_self_healing_recovers_after_feedback(self):
        # Simulation: Attempt 1 has bug, Attempt 2 fixes it after feedback
        attempts = [
            "def solve(): return 1 / 0",  # Div by zero bug
            "def solve(): return 42",  # Fixed
        ]

        def mock_generator(prompt: str, feedback: str | None) -> str:
            return attempts.pop(0)

        def mock_evaluator(code: str) -> EvaluationResult:
            if "1 / 0" in code:
                return EvaluationResult(
                    passed=False,
                    feedback="ZeroDivisionError encountered.",
                    score=0.0,
                )
            return EvaluationResult(passed=True, score=1.0)

        workflow = SelfHealingWorkflow(max_iterations=3)
        final_code, iterations, passed = workflow.run(
            mock_generator, mock_evaluator, "Write solve function"
        )

        assert passed is True
        assert iterations == 2
        assert final_code == "def solve(): return 42"

    def test_self_healing_hits_max_iterations(self):
        # Always fails
        def mock_generator(prompt: str, feedback: str | None) -> str:
            return "def bad(): pass"

        def mock_evaluator(code: str) -> EvaluationResult:
            return EvaluationResult(passed=False, feedback="Still failing")

        workflow = SelfHealingWorkflow(max_iterations=2)
        final_code, iterations, passed = workflow.run(
            mock_generator, mock_evaluator, "Write code"
        )

        assert passed is False
        assert iterations == 2
