import pytest
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from langgraph.checkpoint.memory import MemorySaver

from ai_practice.level1_basics.tool_dispatcher import ToolDispatcher
from ai_practice.level4_agents.react_agent import create_react_agent


class CustomFakeChatModel:
    """Sequential mock LLM that outputs predefined AIMessage responses."""

    def __init__(self, responses: list[AIMessage]) -> None:
        self.responses = list(responses)
        self.call_history: list[list[any]] = []

    def invoke(self, messages: list[any], **kwargs: any) -> AIMessage:
        self.call_history.append(messages)
        if not self.responses:
            return AIMessage(content="No more responses.")
        return self.responses.pop(0)


def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@pytest.mark.unit
class TestReactAgent:
    def test_direct_response_without_tools(self):
        fake_llm = CustomFakeChatModel(
            [AIMessage(content="Hello! How can I help you today?")]
        )
        dispatcher = ToolDispatcher()
        agent = create_react_agent(fake_llm, dispatcher)

        result = agent.invoke({"messages": [HumanMessage(content="Hi")]})
        messages = result["messages"]

        assert len(messages) == 2
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)
        assert messages[1].content == "Hello! How can I help you today?"

    def test_tool_execution_loop(self):
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
        dispatcher = ToolDispatcher()
        dispatcher.register(add)

        agent = create_react_agent(fake_llm, dispatcher)

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

    def test_multi_turn_conversation_with_memory(self):
        fake_llm = CustomFakeChatModel(
            [
                AIMessage(content="I am ready to help."),
                AIMessage(content="Your previous name was Kyungpyo."),
            ]
        )
        dispatcher = ToolDispatcher()
        checkpointer = MemorySaver()
        agent = create_react_agent(fake_llm, dispatcher, checkpointer=checkpointer)

        config = {"configurable": {"thread_id": "session_abc"}}

        # Turn 1
        res1 = agent.invoke(
            {"messages": [HumanMessage(content="My name is Kyungpyo.")]},
            config=config,
        )
        assert len(res1["messages"]) == 2

        # Turn 2 (same thread_id maintains history)
        res2 = agent.invoke(
            {"messages": [HumanMessage(content="Do you remember my name?")]},
            config=config,
        )
        # 2 messages from Turn 1 + 2 messages from Turn 2 = 4 messages
        assert len(res2["messages"]) == 4
        assert res2["messages"][-1].content == "Your previous name was Kyungpyo."

    def test_tool_execution_error_handling(self):
        # LLM calls a tool with invalid arguments
        tool_call_response = AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "add",
                    "args": {"invalid_param": 100},
                    "id": "call_err_1",
                    "type": "tool_call",
                }
            ],
        )
        recovery_response = AIMessage(
            content="I encountered an error with arguments and handled it."
        )

        fake_llm = CustomFakeChatModel([tool_call_response, recovery_response])
        dispatcher = ToolDispatcher()
        dispatcher.register(add)

        agent = create_react_agent(fake_llm, dispatcher)

        result = agent.invoke({"messages": [HumanMessage(content="Run with bad args")]})
        messages = result["messages"]

        assert len(messages) == 4
        assert isinstance(messages[2], ToolMessage)
        assert "error" in messages[2].content.lower()
        assert (
            messages[3].content
            == "I encountered an error with arguments and handled it."
        )

    def test_human_in_the_loop_interruption(self):
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
        dispatcher = ToolDispatcher()
        dispatcher.register(add)

        checkpointer = MemorySaver()
        agent = create_react_agent(
            fake_llm,
            dispatcher,
            checkpointer=checkpointer,
            interrupt_before_tools=True,
        )

        config = {"configurable": {"thread_id": "hitl_thread"}}

        # Step 1: Initial call runs until interrupted before 'tools' node
        agent.invoke(
            {"messages": [HumanMessage(content="Add 50 and 50")]}, config=config
        )

        state = agent.get_state(config)
        assert state.next == ("tools",)  # Paused right before tools node!

        # Step 2: Human approves / resumes by passing None
        res_after = agent.invoke(None, config=config)
        assert res_after["messages"][-1].content == "Sum is 100.0."
