from typing import Annotated, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict

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
    raise NotImplementedError
