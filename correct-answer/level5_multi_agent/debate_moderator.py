from typing import Annotated, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict


class DebateState(TypedDict):
    """State for multi-agent debate with moderator."""

    messages: Annotated[list[BaseMessage], add_messages]
    topic: str
    turn_count: int
    max_turns: int
    consensus: bool
    final_summary: str


def create_debate_system(
    proposer_model: BaseChatModel,
    critic_model: BaseChatModel,
    moderator_model: BaseChatModel,
    max_turns: int = 3,
) -> CompiledStateGraph:
    """Build a multi-agent debate system where proposer and critic debate, and a moderator evaluates.

    Workflow:
    1. Proposer node: Proposes arguments for the topic, increments turn_count.
    2. Critic node: Evaluates proposer's points and raises objections.
    3. Moderator node: Assesses debate. If consensus is reached (contains 'AGREED' or 'CONSENSUS'),
       sets consensus=True and writes final_summary.
    4. Conditional edge from moderator:
       - If consensus == True or turn_count >= max_turns -> END
       - Otherwise -> 'proposer' (next debate round)
    """
    builder = StateGraph(DebateState)

    def proposer_node(state: DebateState) -> dict[str, Any]:
        response = proposer_model.invoke(state["messages"])
        return {
            "messages": [AIMessage(content=str(response.content), name="proposer")],
            "turn_count": state.get("turn_count", 0) + 1,
        }

    def critic_node(state: DebateState) -> dict[str, Any]:
        response = critic_model.invoke(state["messages"])
        return {
            "messages": [AIMessage(content=str(response.content), name="critic")],
        }

    def moderator_node(state: DebateState) -> dict[str, Any]:
        response = moderator_model.invoke(state["messages"])
        content = str(response.content).strip()
        has_consensus = "AGREED" in content.upper() or "CONSENSUS" in content.upper()

        return {
            "messages": [AIMessage(content=content, name="moderator")],
            "consensus": has_consensus,
            "final_summary": content,
        }

    builder.add_node("proposer", proposer_node)
    builder.add_node("critic", critic_node)
    builder.add_node("moderator", moderator_node)

    builder.add_edge(START, "proposer")
    builder.add_edge("proposer", "critic")
    builder.add_edge("critic", "moderator")

    def route_debate(state: DebateState) -> str:
        if state.get("consensus", False) or state.get("turn_count", 0) >= state.get("max_turns", max_turns):
            return END
        return "proposer"

    builder.add_conditional_edges(
        "moderator",
        route_debate,
        {"proposer": "proposer", END: END},
    )

    return builder.compile()
