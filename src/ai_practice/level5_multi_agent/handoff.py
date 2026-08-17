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
    """Create a worker node that can process messages and decide whether to transfer or finish.

    TODO:
    1. model을 호출하여 응답(AIMessage)을 얻습니다.
    2. 응답 내용(raw_text)에서 transfer_options 중 하나가 언급되었는지 확인합니다.
       - 예: "transfer to billing" -> next_agent = "billing"
       - 언급되지 않았거나 완료된 경우 -> next_agent = "FINISH"
    3. State 업데이트 딕셔너리를 반환합니다:
       - messages: [AIMessage(content=raw_text, name=agent_name)]
       - current_agent: agent_name
       - next_agent: 결정된 다음 에이전트 이름 또는 "FINISH"
    """
    valid_targets = set(transfer_options) | {"FINISH"}

    def agent_node(state: HandoffState) -> dict[str, Any]:
        # TODO: 구현하세요
        pass

    return agent_node


def create_handoff_system(
    model: BaseChatModel,
    agents_config: dict[str, list[str]],
    entry_agent: str = "triage",
) -> CompiledStateGraph:
    """Build a decentralized multi-agent system where agents transfer control directly to each other.

    Workflow:
    1. agents_config의 각 에이전트를 노드로 추가합니다 (create_agent_node 활용).
    2. entry_agent를 그래프의 시작점(START)으로 연결합니다.
    3. 각 에이전트 노드에 조건부 엣지(conditional edge)를 설정합니다:
       - next_agent == 'FINISH'이거나 대상이 설정에 없으면 -> END
       - 유효한 대상이면 -> 해당 agent_name 노드로 라우팅
    4. 컴파일하여 반환합니다.
    """
    # TODO: StateGraph(HandoffState)를 구성하고 노드와 조건부 엣지를 연결하세요.
    pass
