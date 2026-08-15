from collections.abc import Sequence
from typing import Annotated, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage
from langchain_core.tools import BaseTool
from langgraph.graph.message import add_messages
from langgraph.graph.state import CompiledStateGraph
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """State for the ReAct agent containing conversation messages."""

    messages: Annotated[list[BaseMessage], add_messages]


def create_react_agent_with_toolnode(
    model: BaseChatModel,
    tools: Sequence[BaseTool | Any],
    checkpointer: Any | None = None,
    interrupt_before_tools: bool = False,
) -> CompiledStateGraph:
    """Build and compile a ReAct agent using LangGraph's prebuilt ToolNode and tools_condition.

    Workflow:
    1. Node 'call_model':
       - Invokes the chat model with current state messages and appends the response.
    2. Node 'tools':
       - Uses `ToolNode(tools)` as the node runner.
    3. Entry point:
       - Set entry point to 'call_model'.
    4. Conditional Edge from 'call_model':
       - Uses `tools_condition` to route to 'tools' or END.
    5. Normal Edge from 'tools':
       - Routes back to 'call_model'.
    6. Compilation:
       - Compile with checkpointer and interrupt_before (if interrupt_before_tools is True).
    """
    # TODO: ToolNode와 tools_condition을 활용하여 StateGraph를 구성하고 컴파일하세요.
    raise NotImplementedError
