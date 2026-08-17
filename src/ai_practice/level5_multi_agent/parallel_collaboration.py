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
    1. model을 호출하여 해당 domain 관점에서 state['topic']을 분석합니다.
    2. {"findings": {domain: 분석_결과_문자열}} 형태의 딕셔너리를 반환합니다.
       (Annotated[dict, operator.or_] 리듀서에 의해 여러 워커의 결과가 자동 병합됩니다.)
    """
    def worker_node(state: ParallelCollaborationState) -> dict[str, Any]:
        # TODO: 구현하세요
        pass

    return worker_node


def create_aggregator_node(
    model: BaseChatModel,
) -> Callable[[ParallelCollaborationState], dict[str, Any]]:
    """Create an aggregator node that synthesizes all domain findings into a final report.

    TODO:
    1. state['findings']에 모인 각 도메인별 분석 결과를 취합하여 model에 전달합니다.
    2. 최종 종합 보고서를 생성하여 {"final_report": 보고서_문자열} 딕셔너리로 반환합니다.
    """
    def aggregator_node(state: ParallelCollaborationState) -> dict[str, Any]:
        # TODO: 구현하세요
        pass

    return aggregator_node


def create_parallel_collaboration_system(
    model: BaseChatModel,
    domains: list[str],
) -> CompiledStateGraph:
    """Build a parallel collaboration graph (Fan-Out -> Fan-In).

    Workflow:
    1. domains의 각 domain에 대해:
       - worker_node를 그래프에 추가합니다.
       - START -> domain 엣지를 추가합니다 (병렬 실행 / Fan-Out).
       - domain -> 'aggregator' 엣지를 추가합니다 (결과 수합 / Fan-In).
    2. 'aggregator' 노드를 추가하고, aggregator -> END 엣지를 연결합니다.
    3. 그래프를 컴파일하여 반환합니다.
    """
    # TODO: StateGraph(ParallelCollaborationState)를 구성하고 노드와 엣지를 연결하세요.
    pass
