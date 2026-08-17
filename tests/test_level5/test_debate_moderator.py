import pytest
from langchain_core.messages import AIMessage, HumanMessage

from ai_practice.level5_multi_agent.debate_moderator import (
    DebateState,
    create_debate_system,
)


class MockLLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)

    def invoke(self, messages: list[any], **kwargs: any) -> AIMessage:
        if not self.responses:
            return AIMessage(content="Default response")
        return AIMessage(content=self.responses.pop(0))


@pytest.mark.unit
class TestDebateModerator:
    def test_debate_stops_on_consensus(self):
        # Round 1: Proposer -> Critic -> Moderator (says CONSENSUS)
        proposer = MockLLM(["Proposal: Microservices architecture is best."])
        critic = MockLLM(["Critique: Monolith is simpler to start with."])
        moderator = MockLLM(["Evaluation: Both agree on modular monolith. CONSENSUS reached."])

        system = create_debate_system(proposer, critic, moderator, max_turns=3)

        initial_state: DebateState = {
            "messages": [HumanMessage(content="Topic: Microservices vs Monolith")],
            "topic": "Architecture",
            "turn_count": 0,
            "max_turns": 3,
            "consensus": False,
            "final_summary": "",
        }

        result = system.invoke(initial_state)

        assert result["turn_count"] == 1
        assert result["consensus"] is True
        assert "CONSENSUS reached." in result["final_summary"]
        # Human -> Proposer -> Critic -> Moderator
        assert len(result["messages"]) == 4

    def test_debate_stops_on_max_turns_limit(self):
        # 2 rounds without consensus
        proposer = MockLLM([
            "Proposal 1",
            "Proposal 2",
        ])
        critic = MockLLM([
            "Critique 1",
            "Critique 2",
        ])
        moderator = MockLLM([
            "Disagreement remains. Continue.",
            "Disagreement remains. Continue.",
        ])

        system = create_debate_system(proposer, critic, moderator, max_turns=2)

        initial_state: DebateState = {
            "messages": [HumanMessage(content="Topic: Tabs vs Spaces")],
            "topic": "Style",
            "turn_count": 0,
            "max_turns": 2,
            "consensus": False,
            "final_summary": "",
        }

        result = system.invoke(initial_state)

        assert result["turn_count"] == 2
        assert result["consensus"] is False
        # Human + (Proposer + Critic + Moderator) * 2 = 1 + 6 = 7
        assert len(result["messages"]) == 7
