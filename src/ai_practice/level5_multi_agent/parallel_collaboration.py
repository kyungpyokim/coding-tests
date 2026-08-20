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
    """Create a worker node that analyzes a topic from its specific domain perspective.

    TODO:
    1. state['topic']이 비어있거나 공백인 경우, 모델을 호출하지 않고
       {"findings": {domain: f"No topic provided for {domain}."}} 딕셔너리를 반환합니다.
    2. 유효한 topic인 경우:
       - f"Analyze the following topic from a {domain} perspective: {state['topic'].strip()}"
         형식으로 프롬프트를 구성합니다.
       - [HumanMessage(content=prompt)] 형태로 model.invoke()를 호출합니다.
       - 응답 내용의 양쪽 공백을 제거(.strip())하여 {"findings": {domain: 분석_결과}} 형태로 반환합니다.
       (Annotated[dict, operator.or_] 리듀서에 의해 여러 워커의 결과가 자동 병합됩니다.)
    """

    def worker_node(state: ParallelCollaborationState) -> dict[str, Any]:
        topic = state.get("topic", "").strip()
        if not topic:
            return {"findings": {domain: f"No topic provided for {domain}."}}

        prompt = f"Analyze the following topic from a {domain} perspective: {topic}"
        response = model.invoke([HumanMessage(content=prompt)])
        return {
            "findings": {domain: str(response.content).strip()},
        }

    return worker_node


def create_aggregator_node(
    model: BaseChatModel,
) -> Callable[[ParallelCollaborationState], dict[str, Any]]:
    """Create an aggregator node that synthesizes all domain findings into a final report.

    TODO:
    1. state.get('findings')가 비어있거나 모든 분석 결과가 비어있는 경우, 모델을 호출하지 않고
       {"final_report": "No findings available to aggregate."} 딕셔너리를 반환합니다.
    2. 유효한 findings가 있는 경우:
       - 각 도메인별 결과를 "- [{domain}]: {result}" 형식의 문자열로 줄바꿈 연결합니다.
       - f"Synthesize these domain findings for '{state.get('topic', '').strip()}' into a final report:\n{findings_text}"
         형식으로 프롬프트를 구성합니다.
       - [HumanMessage(content=prompt)] 형태로 model.invoke()를 호출합니다.
       - 응답 내용의 양쪽 공백을 제거(.strip())하여 {"final_report": 최종_보고서} 딕셔너리로 반환합니다.
    """

    def aggregator_node(state: ParallelCollaborationState) -> dict[str, Any]:
        findings = state.get("findings", {})
        if not findings or not any(str(v).strip() for v in findings.values()):
            return {"final_report": "No findings available to aggregate."}

        findings_text = "\n".join(
            f"- [{domain}]: {result}" for domain, result in findings.items()
        )
        topic = state.get("topic", "").strip()
        prompt = (
            f"Synthesize these domain findings for '{topic}' into a final report:\n"
            f"{findings_text}"
        )
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
    1. 유효성 검증:
       - domains가 비어있으면 ValueError("domains must not be empty.")를 발생시킵니다.
       - domains에 중복이 있으면 ValueError("domains must be unique.")를 발생시킵니다.
    2. domains의 각 domain에 대해:
       - worker_node를 그래프에 추가합니다.
       - START -> domain 엣지를 추가합니다 (병렬 실행 / Fan-Out).
       - domain -> 'aggregator' 엣지를 추가합니다 (결과 수합 / Fan-In).
    3. 'aggregator' 노드를 추가하고, aggregator -> END 엣지를 연결합니다.
    4. 그래프를 컴파일하여 반환합니다.
    """
    if not domains:
        raise ValueError("domains must not be empty.")
    if len(domains) != len(set(domains)):
        raise ValueError("domains must be unique.")

    builder = StateGraph(ParallelCollaborationState)

    for domain in domains:
        builder.add_node(domain, create_worker_node(model, domain))
        builder.add_edge(START, domain)
        builder.add_edge(domain, "aggregator")

    builder.add_node("aggregator", create_aggregator_node(model))
    builder.add_edge("aggregator", END)

    return builder.compile()
