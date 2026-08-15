from collections.abc import Callable
from typing import Annotated, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict


class SupervisorState(TypedDict):
    """State for multi-agent system managed by a supervisor."""

    messages: Annotated[list[BaseMessage], add_messages]
    next: str


def create_supervisor_chain(
    model: BaseChatModel, worker_names: list[str]
) -> Callable[[dict[str, Any]], str]:
    """Create a supervisor router that decides which worker should act next.

    The supervisor returns one of the worker names or 'FINISH'.
    """
    # TODO: model을 호출하여 응답 문자열에서 다음 실행할 worker_name 또는 'FINISH'를 반환하는 함수를 만드세요.
    raise NotImplementedError


def create_multi_agent_system(
    model: BaseChatModel,
    workers: dict[str, Callable[[dict[str, Any]], dict[str, list[BaseMessage]]]],
) -> CompiledStateGraph:
    """Build a multi-agent StateGraph where a supervisor routes tasks to specialized worker nodes.

    Workflow:
    1. Node 'supervisor': Calls create_supervisor_chain to decide the next node.
    2. For each worker in workers:
       - Add node with the worker function.
       - Edge: worker node -> 'supervisor'
    3. Conditional Edge from 'supervisor':
       - If next == 'FINISH' -> END
       - Otherwise -> route to the worker node named state['next']
    """
    # TODO: StateGraph(SupervisorState)를 구성하고 라우팅을 연결하여 컴파일하세요.
    raise NotImplementedError
