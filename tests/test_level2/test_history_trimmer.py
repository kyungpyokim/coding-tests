import pytest
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from ai_practice.level2_state.history_trimmer import estimate_tokens, trim_messages


@pytest.mark.unit
class TestEstimateTokens:
    def test_estimate_empty_string(self):
        assert estimate_tokens("") == 0

    def test_estimate_simple_text(self):
        # 4 chars per token rule of thumb
        assert estimate_tokens("hello world") == 3


@pytest.mark.unit
class TestTrimMessages:
    def test_keep_all_when_under_budget(self):
        messages: list[BaseMessage] = [
            HumanMessage(content="Hi"),
            AIMessage(content="Hello"),
        ]
        result = trim_messages(messages, max_tokens=100)
        assert len(result) == 2
        assert result[0].content == "Hi"
        assert result[1].content == "Hello"

    def test_trim_old_messages_but_preserve_system_message(self):
        messages: list[BaseMessage] = [
            SystemMessage(content="You are a helpful AI assistant."),
            HumanMessage(content="Old question 1"),
            AIMessage(content="Old answer 1"),
            HumanMessage(content="Old question 2"),
            AIMessage(content="Old answer 2"),
            HumanMessage(content="Recent question 3"),
            AIMessage(content="Recent answer 3"),
        ]
        # Set max_tokens to only fit SystemMessage + the latest 2 messages
        result = trim_messages(messages, max_tokens=30, preserve_system=True)

        assert isinstance(result[0], SystemMessage)
        assert result[0].content == "You are a helpful AI assistant."
        # Latest messages should be preserved
        assert result[-1].content == "Recent answer 3"
        assert result[-2].content == "Recent question 3"
        assert len(result) < len(messages)

    def test_empty_messages_returns_empty_list(self):
        assert trim_messages([], max_tokens=50) == []
