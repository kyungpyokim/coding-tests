from typing import Annotated

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class ChatState(TypedDict):
    # add_messages 리듀서를 지정하여 새 메시지 반환 시 기존 리스트에 자동 추가(append)되도록 설정
    messages: Annotated[list[BaseMessage], add_messages]


def run_chat_graph(
    model: BaseChatModel, messages: list[BaseMessage]
) -> list[BaseMessage]:
    """Execute a simple LangGraph StateGraph that calls the model and appends the response."""
    # 1. StateGraph 인스턴스 생성 (상태 스키마 전달)
    graph = StateGraph(ChatState)

    # 2. 챗봇 노드 함수 정의: 모델을 호출하고 추가할 메시지만 딕셔너리로 반환
    def chatbot_node(state: ChatState) -> ChatState:
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    # 3. 노드 등록
    graph.add_node("chatbot", chatbot_node)

    # 4. 엣지(흐름) 연결: START -> chatbot -> END
    graph.add_edge(START, "chatbot")
    graph.add_edge("chatbot", END)

    # 5. 그래프 컴파일 (실행 가능한 Runnable 객체로 변환)
    app = graph.compile()

    # 6. 초기 메시지로 그래프 실행 후 최종 대화 목록 반환
    return app.invoke({"messages": messages})["messages"]
