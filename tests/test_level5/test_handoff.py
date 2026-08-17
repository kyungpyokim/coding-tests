import pytest
from langchain_core.messages import AIMessage, HumanMessage

from ai_practice.level5_multi_agent.handoff import (
    HandoffState,
    create_agent_node,
    create_handoff_system,
)


class MockLLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)

    def invoke(self, messages: list[any], **kwargs: any) -> AIMessage:
        if not self.responses:
            return AIMessage(content="FINISH")
        return AIMessage(content=self.responses.pop(0))


@pytest.mark.unit
class TestHandoffMultiAgent:
    def test_create_agent_node_decision(self):
        fake_model = MockLLM(["I will transfer to billing for your refund request."])
        node = create_agent_node(fake_model, "triage", ["billing", "technical"])

        state: HandoffState = {
            "messages": [HumanMessage(content="I want a refund")],
            "current_agent": "user",
            "next_agent": "",
        }
        update = node(state)

        assert update["current_agent"] == "triage"
        assert update["next_agent"] == "billing"
        assert len(update["messages"]) == 1
        assert update["messages"][0].name == "triage"

    def test_handoff_system_multi_turn_transfer(self):
        # 1. triage -> transfers to technical
        # 2. technical -> resolves problem and FINISH
        model = MockLLM([
            "Let me transfer to technical support for server error.",
            "Technical support: Server restarted. All set! FINISH",
        ])

        agents_config = {
            "triage": ["technical", "billing"],
            "technical": ["billing"],
            "billing": ["technical"],
        }

        system = create_handoff_system(model, agents_config, entry_agent="triage")
        result = system.invoke({
            "messages": [HumanMessage(content="Server 500 error occurred.")],
            "current_agent": "",
            "next_agent": "",
        })

        messages = result["messages"]
        # Human -> triage -> technical
        assert len(messages) == 3
        assert isinstance(messages[0], HumanMessage)
        assert messages[1].name == "triage"
        assert messages[2].name == "technical"
        assert result["current_agent"] == "technical"
        assert result["next_agent"] == "FINISH"
