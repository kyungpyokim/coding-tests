from collections.abc import Callable

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """Evaluation output containing pass status, score, and error feedback."""

    passed: bool
    score: float = Field(default=1.0, ge=0.0, le=1.0)
    feedback: str | None = None


def validate_python_syntax(code_str: str) -> tuple[bool, str | None]:
    """Validate Python code syntax using AST parsing.

    Returns (True, None) if syntax is valid, (False, error_message) otherwise.
    """
    # TODO: ast.parse를 사용하여 문법 오류(SyntaxError)를 검증하세요.
    raise NotImplementedError


class SelfHealingWorkflow:
    """Orchestrates Generator -> Evaluator feedback loop until tests pass or max iterations."""

    def __init__(self, max_iterations: int = 3) -> None:
        self.max_iterations = max_iterations

    def run(
        self,
        generator_fn: Callable[[str, str | None], str],
        evaluator_fn: Callable[[str], EvaluationResult],
        prompt: str,
    ) -> tuple[str, int, bool]:
        """Run iterative generation-evaluation loop.

        Args:
            generator_fn: Takes (prompt, feedback) -> returns generated code
            evaluator_fn: Takes code -> returns EvaluationResult
            prompt: Initial user task prompt

        Returns:
            (final_code, total_iterations, is_successful)
        """
        # TODO: generator_fn과 evaluator_fn을 피드백과 함께 최대 max_iterations 만큼 반복 실행하세요.
        raise NotImplementedError
