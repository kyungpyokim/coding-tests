import pytest
from langchain_core.messages import AIMessage, HumanMessage

from ai_practice.level5_multi_agent.supervisor import (
    create_multi_agent_system,
    create_supervisor_chain,
)


class MockLLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)

    def invoke(self, messages: list[any], **kwargs: any) -> AIMessage:
        if not self.responses:
            return AIMessage(content="FINISH")
        return AIMessage(content=self.responses.pop(0))


@pytest.mark.unit
class TestSupervisorMultiAgent:
    def test_supervisor_chain_routing(self):
        fake_model = MockLLM(["researcher", "FINISH"])
        router = create_supervisor_chain(fake_model, ["researcher", "coder"])

        decision1 = router({"messages": [HumanMessage(content="Find paper")]})
        assert decision1 == "researcher"

        decision2 = router({"messages": [HumanMessage(content="Done")]})
        assert decision2 == "FINISH"

    def test_multi_agent_system_delegation(self):
        # Supervisor decides: 'researcher' -> 'coder' -> 'FINISH'
        supervisor_model = MockLLM(["researcher", "coder", "FINISH"])

        def researcher_node(state):
            return {
                "messages": [
                    AIMessage(
                        content="Research complete: Python 3.12 is fast.",
                        name="researcher",
                    )
                ]
            }

        def coder_node(state):
            return {
                "messages": [
                    AIMessage(
                        content="Code complete: def main(): pass",
                        name="coder",
                    )
                ]
            }

        workers = {
            "researcher": researcher_node,
            "coder": coder_node,
        }

        system = create_multi_agent_system(supervisor_model, workers)
        result = system.invoke(
            {"messages": [HumanMessage(content="Research and write code")]}
        )

        messages = result["messages"]
        # Human -> Researcher -> Coder
        assert len(messages) == 3
        assert isinstance(messages[0], HumanMessage)
        assert messages[1].content == "Research complete: Python 3.12 is fast."
        assert messages[2].content == "Code complete: def main(): pass"
        assert result["next"] == "FINISH"
