from typing import Annotated, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, ToolMessage
from langgraph.graph.message import add_messages
from langgraph.graph.state import END, CompiledStateGraph, StateGraph
from typing_extensions import TypedDict

from ai_practice.core.models import ToolCall
from ai_practice.level1_basics.tool_dispatcher import ToolDispatcher


class AgentState(TypedDict):
    """State for the ReAct agent containing conversation messages."""

    messages: Annotated[list[BaseMessage], add_messages]


def create_react_agent(
    model: BaseChatModel,
    dispatcher: ToolDispatcher,
    checkpointer: Any | None = None,
    interrupt_before_tools: bool = False,
) -> CompiledStateGraph:
    """Build and compile a ReAct agent using LangGraph StateGraph.

    Workflow:
    1. Node 'call_model': Invokes the chat model with current state messages.
    2. Conditional Edge 'should_continue':
       - If the last message is an AIMessage with tool_calls, route to 'tools'.
       - Otherwise, route to END.
    3. Node 'tools': Executes requested tool_calls via ToolDispatcher and appends ToolMessages.
    4. Edge from 'tools' back to 'call_model'.
    5. Optionally pass checkpointer and interrupt_before=["tools"] if interrupt_before_tools is True.
    """

    # 1. 모델 호출 노드: 대화 기록을 모델에 전달하여 응답 메시지를 생성
    def call_model(state: AgentState) -> AgentState:
        return {"messages": [model.invoke(state["messages"])]}

    # 2. 조건부 라우팅 함수: 모델의 마지막 응답에 tool_calls가 있으면 tools 노드로, 없으면 종료(END)
    def should_continue(state: AgentState) -> str:
        last_msg = state["messages"][-1]
        if getattr(last_msg, "tool_calls", None):
            return "tools"
        return END

    # 3. 도구 실행 노드: 모델이 요청한 tool_calls를 실행하고 결과를 ToolMessage로 변환하여 반환
    def tools(state: AgentState) -> AgentState:
        last_msg = state["messages"][-1]
        tool_messages = []

        for tc in last_msg.tool_calls:
            # ToolCall 객체 생성 및 ToolDispatcher를 통한 도구 실행
            call_obj = ToolCall(
                name=tc["name"],
                arguments=tc["args"],
                call_id=tc.get("id"),
            )
            result = dispatcher.execute(call_obj)

            # 실행 성공/실패 여부에 따라 결과 텍스트 구성
            if result.status == "success":
                content = str(result.output)
            else:
                content = f"Error: {result.error_message}"

            # tool_call_id와 매칭되는 ToolMessage 생성
            tool_messages.append(
                ToolMessage(content=content, tool_call_id=tc.get("id"))
            )

        return {"messages": tool_messages}

    # 4. StateGraph 인스턴스 생성 및 노드 등록
    graph = StateGraph(AgentState)
    graph.add_node("call_model", call_model)
    graph.add_node("tools", tools)

    # 5. 엣지 연결 및 진입점 설정
    graph.set_entry_point("call_model")
    graph.add_conditional_edges("call_model", should_continue)  # 모델 판단에 따라 분기
    graph.add_edge("tools", "call_model")  # 도구 실행 후 다시 모델로 피드백

    # 6. Human-in-the-loop 옵션: 도구 실행 전 일시 중단 설정
    interrupt_before = ["tools"] if interrupt_before_tools else None

    # 7. 그래프 컴파일 및 반환 (체크포인터 메모리 및 인터럽트 옵션 적용)
    return graph.compile(checkpointer=checkpointer, interrupt_before=interrupt_before)
