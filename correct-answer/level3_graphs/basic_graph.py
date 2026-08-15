from typing import Annotated

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


def run_chat_graph(
    model: BaseChatModel, messages: list[BaseMessage]
) -> list[BaseMessage]:
    """Execute a simple LangGraph StateGraph that calls the model and appends the response."""
    builder = StateGraph(ChatState)

    def chatbot(state: ChatState) -> dict[str, list[BaseMessage]]:
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    builder.add_node("chatbot", chatbot)
    builder.add_edge(START, "chatbot")
    builder.add_edge("chatbot", END)

    graph = builder.compile()
    final_state = graph.invoke({"messages": messages})
    return final_state["messages"]
