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

    # TODO: StateGraph(AgentState)를 구성하고 노드/엣지를 연결하여 컴파일하세요.
    def call_model(state: AgentState) -> AgentState:
        return {"messages": [model.invoke(state["messages"])]}

    def should_continue(state: AgentState) -> str:
        last_msg = state["messages"][-1]
        if getattr(last_msg, "tool_calls", None):
            return "tools"
        return END

    def tools(state: AgentState) -> AgentState:
        last_msg = state["messages"][-1]
        tool_messages = []

        for tc in last_msg.tool_calls:
            call_obj = ToolCall(
                name=tc["name"],
                arguments=tc["args"],
                call_id=tc.get("id"),
            )
            result = dispatcher.execute(call_obj)

            if result.status == "success":
                content = str(result.output)
            else:
                content = f"Error: {result.error_message}"

            tool_messages.append(
                ToolMessage(content=content, tool_call_id=tc.get("id"))
            )

        return {"messages": tool_messages}

    graph = StateGraph(AgentState)

    graph.add_node("call_model", call_model)
    graph.add_node("tools", tools)

    graph.set_entry_point("call_model")
    graph.add_conditional_edges("call_model", should_continue)
    graph.add_edge("tools", "call_model")

    interrupt_before = ["tools"] if interrupt_before_tools else None

    return graph.compile(checkpointer=checkpointer, interrupt_before=interrupt_before)
