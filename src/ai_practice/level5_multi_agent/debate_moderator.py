from typing import Annotated, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph, StateGraph, START, END
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
    1. Proposer node:
       - proposer_model을 호출하여 주장을 제시/보완합니다.
       - turn_count를 1 증가시키고, AIMessage(content=..., name="proposer")를 반환합니다.
    2. Critic node:
       - critic_model을 호출하여 제안에 대한 비판/반론을 제기합니다.
       - AIMessage(content=..., name="critic")를 반환합니다.
    3. Moderator node:
       - moderator_model을 호출하여 토론 내용을 종합 평가합니다.
       - 응답 내용에 "AGREED" 또는 "CONSENSUS"가 포함되어 있으면 consensus=True로 설정합니다.
       - final_summary에 평가 내용을 저장하고 AIMessage(content=..., name="moderator")를 반환합니다.
    4. Graph 연결 및 조건부 엣지:
       - START -> "proposer" -> "critic" -> "moderator"
       - "moderator"에서 조건부 분기:
         - consensus == True 이거나 turn_count >= max_turns 이면 -> END
         - 그렇지 않으면 -> "proposer"로 돌아가 다음 라운드 진행
    """

    # TODO: StateGraph(DebateState)를 구성하고 노드와 조건부 엣지를 연결하세요.
    def proposer_node(state: DebateState) -> dict[str, Any]:
        res = proposer_model.invoke(state["messages"])
        ai_message = AIMessage(content=str(res.content), name="proposer")
        return {
            "messages": [ai_message],
            "turn_count": state["turn_count"] + 1,
        }

    def critic_node(state: DebateState) -> dict[str, Any]:
        res = critic_model.invoke(state["messages"])
        ai_message = AIMessage(content=str(res.content), name="critic")
        return {
            "messages": [ai_message],
        }

    def moderator_node(state: DebateState) -> dict[str, Any]:
        res = moderator_model.invoke(state['messages'])
        content = str(res.content).strip()
        ai_message = AIMessage(content=content, name='moderator')

        return {
            'messages': [ai_message],
            'final_summary': content,
            'consensus': "AGREED" in content.upper() or "CONSENSUS" in content.upper()
        }

    builder = StateGraph(DebateState)

    builder.add_node('proposer_node', proposer_node)
    builder.add_node('critic_node', critic_node)
    builder.add_node('moderator_node', moderator_node)

    builder.add_edge(START, 'proposer_node')
    builder.add_edge('proposer_node', 'critic_node')
    builder.add_edge('critic_node', 'moderator_node')

    def route(state: DebateState) -> str:
        if state['consensus'] or state['turn_count'] >= state['max_turns']:
            return END
        
        return 'proposer_node'

    builder.add_conditional_edges('moderator_node', route)

    return builder.compile()


