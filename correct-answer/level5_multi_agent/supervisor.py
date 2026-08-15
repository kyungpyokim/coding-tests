from collections.abc import Callable
from typing import Annotated, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph
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
    """Create a supervisor router that decides which worker should act next."""
    valid_options = set(worker_names) | {"FINISH"}

    def route(state: dict[str, Any]) -> str:
        response = model.invoke(state["messages"])
        raw_text = str(response.content).strip()

        for option in valid_options:
            if option.lower() in raw_text.lower():
                return option
        return "FINISH"

    return route


def create_multi_agent_system(
    model: BaseChatModel,
    workers: dict[str, Callable[[dict[str, Any]], dict[str, list[BaseMessage]]]],
) -> CompiledStateGraph:
    """Build a multi-agent StateGraph where a supervisor routes tasks to specialized worker nodes."""
    worker_names = list(workers.keys())
    router_fn = create_supervisor_chain(model, worker_names)

    builder = StateGraph(SupervisorState)

    def supervisor_node(state: SupervisorState) -> dict[str, str]:
        next_step = router_fn(state)
        return {"next": next_step}

    builder.add_node("supervisor", supervisor_node)

    for name, worker_fn in workers.items():
        builder.add_node(name, worker_fn)
        builder.add_edge(name, "supervisor")

    builder.add_edge(START, "supervisor")

    def route_decision(state: SupervisorState) -> str:
        if state["next"] == "FINISH" or state["next"] not in workers:
            return END
        return state["next"]

    routing_map = {name: name for name in worker_names}
    routing_map[END] = END

    builder.add_conditional_edges("supervisor", route_decision, routing_map)

    return builder.compile()
