import operator
from collections.abc import Callable
from typing import Annotated, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict


class ParallelCollaborationState(TypedDict):
    """State for parallel multi-agent collaboration."""

    topic: str
    findings: Annotated[dict[str, str], operator.or_]
    final_report: str


def create_worker_node(
    model: BaseChatModel,
    domain: str,
) -> Callable[[ParallelCollaborationState], dict[str, Any]]:
    """Create a worker node that analyzes a topic from its specific domain perspective."""

    def worker_node(state: ParallelCollaborationState) -> dict[str, Any]:
        prompt = f"Analyze the following topic from a {domain} perspective: {state['topic']}"
        response = model.invoke([HumanMessage(content=prompt)])
        return {
            "findings": {domain: str(response.content).strip()},
        }

    return worker_node


def create_aggregator_node(
    model: BaseChatModel,
) -> Callable[[ParallelCollaborationState], dict[str, Any]]:
    """Create an aggregator node that synthesizes all domain findings into a final report."""

    def aggregator_node(state: ParallelCollaborationState) -> dict[str, Any]:
        findings_text = "\n".join(
            f"- [{domain}]: {result}" for domain, result in state["findings"].items()
        )
        prompt = f"Synthesize these domain findings for '{state['topic']}' into a final report:\n{findings_text}"
        response = model.invoke([HumanMessage(content=prompt)])
        return {
            "final_report": str(response.content).strip(),
        }

    return aggregator_node


def create_parallel_collaboration_system(
    model: BaseChatModel,
    domains: list[str],
) -> CompiledStateGraph:
    """Build a parallel collaboration graph (Fan-Out -> Fan-In).

    Workflow:
    1. START fans out to all domain worker nodes in parallel.
    2. Each worker node performs analysis and updates state['findings'].
    3. All worker nodes fan in to the 'aggregator' node.
    4. Aggregator synthesizes the findings into state['final_report'] and routes to END.
    """
    builder = StateGraph(ParallelCollaborationState)

    for domain in domains:
        worker_fn = create_worker_node(model, domain)
        builder.add_node(domain, worker_fn)
        builder.add_edge(START, domain)
        builder.add_edge(domain, "aggregator")

    aggregator_fn = create_aggregator_node(model)
    builder.add_node("aggregator", aggregator_fn)
    builder.add_edge("aggregator", END)

    return builder.compile()
