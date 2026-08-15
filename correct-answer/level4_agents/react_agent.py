from typing import Annotated, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
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
    """Build and compile a ReAct agent using LangGraph StateGraph."""
    builder = StateGraph(AgentState)

    # 1. 모델 호출 노드
    def call_model(state: AgentState) -> dict[str, list[BaseMessage]]:
        response = model.invoke(state["messages"])
        return {"messages": [response]}

    # 2. 다음 노드 결정 조건부 엣지
    def should_continue(state: AgentState) -> str:
        last_message = state["messages"][-1]
        if isinstance(last_message, AIMessage) and getattr(
            last_message, "tool_calls", None
        ):
            return "tools"
        return END

    # 3. 도구 실행 노드
    def call_tools(state: AgentState) -> dict[str, list[BaseMessage]]:
        last_message = state["messages"][-1]
        tool_messages: list[BaseMessage] = []

        for tc in getattr(last_message, "tool_calls", []):
            call_id = tc.get("id")
            tool_name = tc.get("name", "")
            arguments = tc.get("args", {})

            tool_call = ToolCall(name=tool_name, arguments=arguments, call_id=call_id)
            result = dispatcher.execute(tool_call)

            content = (
                str(result.output)
                if result.status == "success"
                else f"Error: {result.error_message}"
            )
            tool_messages.append(
                ToolMessage(
                    content=content,
                    tool_call_id=call_id or "",
                    name=tool_name,
                )
            )

        return {"messages": tool_messages}

    builder.add_node("call_model", call_model)
    builder.add_node("tools", call_tools)

    builder.add_edge(START, "call_model")
    builder.add_conditional_edges(
        "call_model",
        should_continue,
        {"tools": "tools", END: END},
    )
    builder.add_edge("tools", "call_model")

    interrupt_before = ["tools"] if interrupt_before_tools else None

    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=interrupt_before,
    )
