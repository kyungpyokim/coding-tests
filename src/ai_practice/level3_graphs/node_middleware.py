from collections.abc import Callable, Sequence
from typing import Annotated, Any, Protocol

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict


class NodeMiddleware(Protocol):
    """Protocol defining lifecycle hooks for LangGraph node middleware."""

    def before_node(
        self, node_name: str, state: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Executed before the node function runs."""
        ...

    def after_node(
        self, node_name: str, state: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any] | None:
        """Executed after the node function successfully completes."""
        ...

    def on_node_error(
        self, node_name: str, state: dict[str, Any], error: Exception
    ) -> dict[str, Any] | None:
        """Executed when the node function raises an exception."""
        ...


# ============================================================================
# [패턴 1] 개별 노드 데코레이터 / 래퍼 함수 (Node Decorator Pattern)
# ============================================================================
def wrap_node_with_middleware(
    node_name: str,
    node_func: Callable[[dict[str, Any]], dict[str, Any]],
    middlewares: Sequence[NodeMiddleware],
) -> Callable[[dict[str, Any]], dict[str, Any]]:
    """Wrap a LangGraph node function with a pipeline of middlewares."""

    def wrapped(state: dict[str, Any]) -> dict[str, Any]:
        cur_state = dict(state)

        for mw in middlewares:
            res = mw.before_node(node_name, cur_state)
            if isinstance(res, dict):
                cur_state.update(res)

        try:
            result = node_func(cur_state)
        except Exception as e:
            for mw in middlewares:
                recovery = mw.on_node_error(node_name, cur_state, e)
                if isinstance(recovery, dict):
                    return recovery
            raise e

        cur_result = dict(result)
        for mw in middlewares:
            res = mw.after_node(node_name, cur_state, cur_result)
            if isinstance(res, dict):
                cur_result.update(res)

        return cur_result

    return wrapped


# ============================================================================
# [패턴 2] 메인 StateGraph에 미들웨어 일괄 주입 (Graph-level Middleware Applicator)
# ============================================================================
def apply_middlewares_to_graph(
    graph: StateGraph,
    global_middlewares: Sequence[NodeMiddleware] | None = None,
    node_middlewares: dict[str, Sequence[NodeMiddleware]] | None = None,
) -> StateGraph:
    """Apply global and node-specific middlewares to all registered nodes in a main StateGraph.

    Workflow:
    1. Iterate over all nodes in `graph.nodes`.
    2. For each node, combine `global_middlewares` with any specific middlewares from `node_middlewares.get(node_name, [])`.
    3. If middlewares exist for the node:
       - Wrap the node's original runnable execution using `wrap_node_with_middleware`.
       - Replace the node's runnable in `graph.nodes[node_name]` with the wrapped `RunnableLambda`.
    4. Return the modified `graph`.
    """
    # TODO: 메인 StateGraph의 노드들을 순회하여 미들웨어를 일괄 주입하세요.
    raise NotImplementedError


# ============================================================================
# [패턴 3] 가드레일 / 전처리 독립 노드 파이프라인 (Guardrail Pipeline Node Pattern)
# ============================================================================
class GuardedChatState(TypedDict):
    """State for guarded chat graph pipeline."""

    messages: Annotated[list[BaseMessage], add_messages]
    blocked: bool


def create_guarded_chat_graph(
    model: BaseChatModel,
    guardrail_mw: NodeMiddleware,
) -> CompiledStateGraph:
    """Build a StateGraph with dedicated guardrail pipeline nodes directly in the graph flow.

    Workflow:
    1. Node 'input_guardrail':
       - Executes `guardrail_mw.before_node('input_guardrail', state)`.
       - If guardrail returns a dict, return it; otherwise return {'blocked': False}.
    2. Node 'chatbot':
       - Invokes `model` with current `state['messages']` and returns `{'messages': [response]}`.
    3. Conditional Edge from 'input_guardrail':
       - If `state.get('blocked')` is True -> route directly to END.
       - Otherwise -> route to 'chatbot'.
    4. Edge:
       - START -> 'input_guardrail'
       - 'chatbot' -> END
    5. Compile and return the graph.
    """
    # TODO: StateGraph(GuardedChatState)에 가드레일 노드와 챗봇 노드를 배치하고 컴파일하세요.
    raise NotImplementedError
