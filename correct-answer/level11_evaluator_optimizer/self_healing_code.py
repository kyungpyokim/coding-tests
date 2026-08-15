import ast
from collections.abc import Callable

from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """Evaluation output containing pass status, score, and error feedback."""

    passed: bool
    score: float = Field(default=1.0, ge=0.0, le=1.0)
    feedback: str | None = None


def validate_python_syntax(code_str: str) -> tuple[bool, str | None]:
    """Validate Python code syntax using AST parsing."""
    try:
        ast.parse(code_str)
        return True, None
    except SyntaxError as e:
        return False, str(e)


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
        """Run iterative generation-evaluation loop."""
        feedback: str | None = None
        code: str = ""

        for iteration in range(1, self.max_iterations + 1):
            code = generator_fn(prompt, feedback)
            eval_result = evaluator_fn(code)

            if eval_result.passed:
                return code, iteration, True

            feedback = eval_result.feedback

        return code, self.max_iterations, False
