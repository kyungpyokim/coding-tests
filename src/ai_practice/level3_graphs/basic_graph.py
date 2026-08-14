from typing import Annotated

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def run_chat_graph(
    model: BaseChatModel, messages: list[BaseMessage]
) -> list[BaseMessage]:
    """Execute a simple LangGraph StateGraph that calls the model and appends the response."""
    # TODO: StateGraph(ChatState)를 생성하고, model을 호출하는 챗봇 노드를 등록한 뒤 컴파일하여 실행하세요.
    raise NotImplementedError
