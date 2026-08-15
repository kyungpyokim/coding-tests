from collections.abc import Callable, Sequence
from typing import Any, Protocol


class NodeMiddleware(Protocol):
    """Protocol defining lifecycle hooks for LangGraph node middleware."""

    def before_node(
        self, node_name: str, state: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Executed before the node function runs.

        - Can return an updated state dict (or None to keep state as-is).
        - Can raise an exception to block node execution.
        """
        ...

    def after_node(
        self, node_name: str, state: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Executed after the node function successfully completes.

        - Can return an updated result dict (or None to keep result as-is).
        """
        ...

    def on_node_error(
        self, node_name: str, state: dict[str, Any], error: Exception
    ) -> dict[str, Any] | None:
        """Executed when the node function raises an exception.

        - Can return a fallback result dict to recover from error.
        - Can return None or re-raise to propagate the exception.
        """
        ...


def wrap_node_with_middleware(
    node_name: str,
    node_func: Callable[[dict[str, Any]], dict[str, Any]],
    middlewares: Sequence[NodeMiddleware],
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Wrap a LangGraph node function with a pipeline of middlewares.

    Workflow:
    1. Before Execution:
       - Iterate through middlewares in order and call `before_node(node_name, current_state)`.
       - If a middleware returns a dict, update `current_state` with the returned values.
    2. Node Execution:
       - Execute `node_func(current_state)`.
    3. After Execution (on success):
       - Iterate through middlewares in order and call `after_node(node_name, current_state, current_result)`.
       - If a middleware returns a dict, update `current_result` with the returned values.
       - Return `current_result`.
    4. Error Handling (on exception):
       - Iterate through middlewares and call `on_node_error(node_name, current_state, exc)`.
       - If any middleware returns a recovery dict, treat it as the final result and return it.
       - If no middleware handles the error, re-raise the exception.
    """
    # TODO: 위 workflow에 따라 미들웨어 파이프라인을 실행하는 래퍼 함수를 구현하세요.
    raise NotImplementedError
