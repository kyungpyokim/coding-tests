from collections.abc import Callable
from typing import Annotated, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict


class HandoffState(TypedDict):
    """State for peer-to-peer agent handoff system."""

    messages: Annotated[list[BaseMessage], add_messages]
    current_agent: str
    next_agent: str


def create_agent_node(
    model: BaseChatModel,
    agent_name: str,
    transfer_options: list[str],
) -> Callable[[HandoffState], dict[str, Any]]:
    """Create a worker node that can process messages and decide whether to transfer or finish."""
    valid_targets = set(transfer_options) | {"FINISH"}

    def agent_node(state: HandoffState) -> dict[str, Any]:
        response = model.invoke(state["messages"])
        raw_text = str(response.content).strip()

        chosen_next = "FINISH"
        for target in valid_targets:
            if f"transfer_to_{target.lower()}" in raw_text.lower() or target.lower() in raw_text.lower():
                chosen_next = target
                break

        ai_message = AIMessage(content=raw_text, name=agent_name)
        return {
            "messages": [ai_message],
            "current_agent": agent_name,
            "next_agent": chosen_next,
        }

    return agent_node


def create_handoff_system(
    model: BaseChatModel,
    agents_config: dict[str, list[str]],
    entry_agent: str = "triage",
) -> CompiledStateGraph:
    """Build a decentralized multi-agent system where agents transfer control directly to each other.

    Workflow:
    1. Each agent in agents_config is added as a node.
    2. Each agent node has conditional edges:
       - If next_agent == 'FINISH' -> END
       - If next_agent is valid agent in agents_config -> next_agent
       - Otherwise -> END
    3. Graph starts at entry_agent.
    """
    builder = StateGraph(HandoffState)

    for agent_name, transfer_options in agents_config.items():
        node_fn = create_agent_node(model, agent_name, transfer_options)
        builder.add_node(agent_name, node_fn)

    builder.add_edge(START, entry_agent)

    def route_handoff(state: HandoffState) -> str:
        next_target = state.get("next_agent", "FINISH")
        if next_target == "FINISH" or next_target not in agents_config:
            return END
        return next_target

    for agent_name, transfer_options in agents_config.items():
        routing_map = {opt: opt for opt in transfer_options if opt in agents_config}
        routing_map[END] = END
        builder.add_conditional_edges(agent_name, route_handoff, routing_map)

    return builder.compile()
