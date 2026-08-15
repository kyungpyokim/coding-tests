from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver

from ai_practice.level4_agents.react_agent_toolnode import (
    create_react_agent_with_toolnode,
)


class CustomFakeChatModel:
    """Sequential mock LLM that outputs predefined AIMessage responses."""

    def __init__(self, responses: list[AIMessage]) -> None:
        self.responses = list(responses)
        self.call_history: list[list[Any]] = []

    def invoke(self, messages: list[Any], **kwargs: Any) -> AIMessage:
        self.call_history.append(messages)
        if not self.responses:
            return AIMessage(content="No more responses.")
        return self.responses.pop(0)


@tool
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@pytest.mark.unit
class TestReactAgentToolNode:
    def test_direct_response_without_tools(self) -> None:
        fake_llm = CustomFakeChatModel(
            [AIMessage(content="Hello! How can I help you today?")]
        )
        agent = create_react_agent_with_toolnode(fake_llm, [add, multiply])

        result = agent.invoke({"messages": [HumanMessage(content="Hi")]})
        messages = result["messages"]

        assert len(messages) == 2
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)
        assert messages[1].content == "Hello! How can I help you today?"

    def test_tool_execution_loop(self) -> None:
        # 1. LLM requests tool call
        tool_call_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "add",
                    "args": {"a": 10.0, "b": 25.0},
                    "id": "call_add_1",
                    "type": "tool_call",
                }
            ],
        )
        # 2. LLM gives final answer after observing tool result
        final_response = AIMessage(content="The result of 10 + 25 is 35.0.")

        fake_llm = CustomFakeChatModel([tool_call_response, final_response])
        agent = create_react_agent_with_toolnode(fake_llm, [add])

        result = agent.invoke({"messages": [HumanMessage(content="Calculate 10 + 25")]})
        messages = result["messages"]

        # Expected flow: Human -> AI(tool_call) -> ToolMessage -> AI(final)
        assert len(messages) == 4
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)
        assert len(messages[1].tool_calls) == 1

        assert isinstance(messages[2], ToolMessage)
        assert messages[2].tool_call_id == "call_add_1"
        assert messages[2].content == "35.0"

        assert isinstance(messages[3], AIMessage)
        assert messages[3].content == "The result of 10 + 25 is 35.0."

    def test_parallel_tool_calls(self) -> None:
        # 1. LLM requests multiple tool calls in a single turn
        multi_tool_call = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "add",
                    "args": {"a": 5.0, "b": 3.0},
                    "id": "call_add_1",
                    "type": "tool_call",
                },
                {
                    "name": "multiply",
                    "args": {"a": 4.0, "b": 2.0},
                    "id": "call_mul_1",
                    "type": "tool_call",
                },
            ],
        )
        final_response = AIMessage(content="5+3 is 8 and 4*2 is 8.")

        fake_llm = CustomFakeChatModel([multi_tool_call, final_response])
        agent = create_react_agent_with_toolnode(fake_llm, [add, multiply])

        result = agent.invoke(
            {"messages": [HumanMessage(content="Calculate 5+3 and 4*2")]}
        )
        messages = result["messages"]

        # Expected flow: Human -> AI(2 tool calls) -> ToolMessage(add) -> ToolMessage(mul) -> AI(final)
        assert len(messages) == 5
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)
        assert len(messages[1].tool_calls) == 2

        assert isinstance(messages[2], ToolMessage)
        assert isinstance(messages[3], ToolMessage)
        tool_ids = {messages[2].tool_call_id, messages[3].tool_call_id}
        assert tool_ids == {"call_add_1", "call_mul_1"}

        assert isinstance(messages[4], AIMessage)
        assert messages[4].content == "5+3 is 8 and 4*2 is 8."

    def test_multi_turn_conversation_with_memory(self) -> None:
        fake_llm = CustomFakeChatModel(
            [
                AIMessage(content="I am ready to help."),
                AIMessage(content="Your previous name was Kyungpyo."),
            ]
        )
        checkpointer = MemorySaver()
        agent = create_react_agent_with_toolnode(
            fake_llm, [add], checkpointer=checkpointer
        )

        config = {"configurable": {"thread_id": "session_toolnode_123"}}

        # Turn 1
        res1 = agent.invoke(
            {"messages": [HumanMessage(content="My name is Kyungpyo.")]},
            config=config,
        )
        assert len(res1["messages"]) == 2

        # Turn 2
        res2 = agent.invoke(
            {"messages": [HumanMessage(content="Do you remember my name?")]},
            config=config,
        )
        assert len(res2["messages"]) == 4
        assert res2["messages"][-1].content == "Your previous name was Kyungpyo."

    def test_human_in_the_loop_interruption(self) -> None:
        tool_call_response = AIMessage(
            content="Executing addition...",
            tool_calls=[
                {
                    "name": "add",
                    "args": {"a": 50.0, "b": 50.0},
                    "id": "call_hitl_1",
                    "type": "tool_call",
                }
            ],
        )
        final_response = AIMessage(content="Sum is 100.0.")

        fake_llm = CustomFakeChatModel([tool_call_response, final_response])
        checkpointer = MemorySaver()
        agent = create_react_agent_with_toolnode(
            fake_llm,
            [add],
            checkpointer=checkpointer,
            interrupt_before_tools=True,
        )

        config = {"configurable": {"thread_id": "hitl_toolnode_thread"}}

        # Step 1: Run until paused before 'tools' node
        agent.invoke(
            {"messages": [HumanMessage(content="Add 50 and 50")]}, config=config
        )

        state = agent.get_state(config)
        assert state.next == ("tools",)  # Paused right before tools node!

        # Step 2: Resume by passing None
        res_after = agent.invoke(None, config=config)
        assert res_after["messages"][-1].content == "Sum is 100.0."
