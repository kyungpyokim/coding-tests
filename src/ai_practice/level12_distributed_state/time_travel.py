from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict


class TimeTravelState(TypedDict):
    """State tracked by checkpointer for time-travel debugging."""

    messages: Annotated[list[BaseMessage], add_messages]
    step_count: int


def build_time_travel_graph(checkpointer: MemorySaver) -> CompiledStateGraph:
    """Build a StateGraph connected to MemorySaver for snapshot history tracking."""
    # TODO: StateGraph(TimeTravelState)를 생성하고 단계마다 step_count를 1씩 증가시키는 노드를 연결하여 컴파일하세요.
    raise NotImplementedError


def get_state_history(
    graph: CompiledStateGraph, thread_id: str
) -> list[dict[str, Any]]:
    """Retrieve all snapshot checkpoints for the given thread_id."""
    # TODO: graph.get_state_history(config)를 순회하여 checkpoint_id와 state values 목록을 반환하세요.
    raise NotImplementedError


def rollback_and_branch(
    graph: CompiledStateGraph,
    thread_id: str,
    target_checkpoint_id: str,
    new_message: BaseMessage,
) -> list[BaseMessage]:
    """Roll back to target_checkpoint_id and branch off with a new message."""
    # TODO: target_checkpoint_id가 지정된 config로 graph.invoke하여 과거 시점에서 분기된 새 상태를 반환하세요.
    raise NotImplementedError
