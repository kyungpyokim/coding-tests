import pytest
from langchain_core.language_models import FakeListChatModel
from langchain_core.messages import AIMessage, HumanMessage

from ai_practice.level3_graphs.basic_graph import run_chat_graph


@pytest.mark.unit
class TestBasicChatGraph:
    def test_graph_executes_and_appends_response(self):
        fake_llm = FakeListChatModel(responses=["Hello! I am ready to help."])
        initial_messages = [HumanMessage(content="Hello AI")]

        result_messages = run_chat_graph(fake_llm, initial_messages)

        assert len(result_messages) == 2
        assert isinstance(result_messages[0], HumanMessage)
        assert isinstance(result_messages[1], AIMessage)
        assert result_messages[1].content == "Hello! I am ready to help."
