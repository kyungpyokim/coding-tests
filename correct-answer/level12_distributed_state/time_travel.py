from typing import Annotated, Any

from langchain_core.messages import BaseMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict


class TimeTravelState(TypedDict):
    """State tracked by checkpointer for time-travel debugging."""

    messages: Annotated[list[BaseMessage], add_messages]
    step_count: int


def build_time_travel_graph(checkpointer: MemorySaver) -> CompiledStateGraph:
    """Build a StateGraph connected to MemorySaver for snapshot history tracking."""
    builder = StateGraph(TimeTravelState)

    def process_node(state: TimeTravelState) -> dict[str, Any]:
        count = state.get("step_count", 0) + 1
        return {"step_count": count}

    builder.add_node("process", process_node)
    builder.add_edge(START, "process")
    builder.add_edge("process", END)

    return builder.compile(checkpointer=checkpointer)


def get_state_history(
    graph: CompiledStateGraph, thread_id: str
) -> list[dict[str, Any]]:
    """Retrieve all snapshot checkpoints for the given thread_id."""
    config = {"configurable": {"thread_id": thread_id}}
    snapshots: list[dict[str, Any]] = []

    for state in graph.get_state_history(config):
        checkpoint_id = state.config["configurable"].get("checkpoint_id")
        snapshots.append(
            {
                "checkpoint_id": checkpoint_id,
                "values": state.values,
                "next": state.next,
            }
        )
    return snapshots


def rollback_and_branch(
    graph: CompiledStateGraph,
    thread_id: str,
    target_checkpoint_id: str,
    new_message: BaseMessage,
) -> list[BaseMessage]:
    """Roll back to target_checkpoint_id and branch off with a new message."""
    config = {
        "configurable": {
            "thread_id": thread_id,
            "checkpoint_id": target_checkpoint_id,
        }
    }
    result = graph.invoke({"messages": [new_message]}, config=config)
    return result["messages"]
