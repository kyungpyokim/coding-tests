from collections.abc import Callable
from typing import Annotated, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.constants import END
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph, StateGraph
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
    valid_name = set(worker_names) | {"FINISH"}

    def route(state: dict[str, Any]) -> str:
        res = model.invoke(state["messages"])
        raw_text = str(res.content).strip()

        for name in valid_name:
            if name.lower() in raw_text.lower():
                return name
        return "FINISH"

    return route


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
    worker_names = list(workers.keys())
    route_fn = create_supervisor_chain(model, worker_names)

    builder = StateGraph(SupervisorState)

    def supervisor(state: SupervisorState) -> dict[str, str]:
        next = route_fn(state)
        return {"next": next}

    def route(state: SupervisorState) -> str:
        if state["next"] == "FINISH" or state["next"] not in workers:
            return END

        return state["next"]

    builder.add_node("supervisor", supervisor)

    for name, worker_fn in workers.items():
        builder.add_node(name, worker_fn)
        builder.add_edge(name, "supervisor")

    builder.set_entry_point("supervisor")

    routing_map = {name: name for name in worker_names}
    routing_map[END] = END

    builder.add_conditional_edges("supervisor", route, routing_map)

    return builder.compile()
