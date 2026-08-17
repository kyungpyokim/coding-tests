import pytest
from langchain_core.messages import AIMessage

from ai_practice.level5_multi_agent.parallel_collaboration import (
    ParallelCollaborationState,
    create_aggregator_node,
    create_parallel_collaboration_system,
    create_worker_node,
)


class MockLLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)

    def invoke(self, messages: list[any], **kwargs: any) -> AIMessage:
        if not self.responses:
            return AIMessage(content="Default mock output")
        return AIMessage(content=self.responses.pop(0))


@pytest.mark.unit
class TestParallelCollaboration:
    def test_worker_node_output(self):
        model = MockLLM(["Technical feasibility is high."])
        worker = create_worker_node(model, "tech")

        state: ParallelCollaborationState = {
            "topic": "AI Automation",
            "findings": {},
            "final_report": "",
        }
        result = worker(state)
        assert result == {"findings": {"tech": "Technical feasibility is high."}}

    def test_aggregator_node_synthesis(self):
        model = MockLLM(["Synthesis: High ROI with manageable technical hurdles."])
        aggregator = create_aggregator_node(model)

        state: ParallelCollaborationState = {
            "topic": "AI Automation",
            "findings": {
                "tech": "Technical feasibility is high.",
                "finance": "Initial investment 10k, ROI expected in 6 months.",
            },
            "final_report": "",
        }
        result = aggregator(state)
        assert result == {"final_report": "Synthesis: High ROI with manageable technical hurdles."}

    def test_parallel_collaboration_fan_out_fan_in(self):
        # 2 workers + 1 aggregator
        model = MockLLM([
            "Tech: Feasible with LangGraph.",
            "Market: Growing at 40% CAGR.",
            "Final Report: Strong market demand with solid tech foundations.",
        ])

        domains = ["tech", "market"]
        system = create_parallel_collaboration_system(model, domains)

        initial_state: ParallelCollaborationState = {
            "topic": "Multi-Agent Frameworks",
            "findings": {},
            "final_report": "",
        }

        result = system.invoke(initial_state)

        assert "tech" in result["findings"]
        assert "market" in result["findings"]
        assert result["findings"]["tech"] == "Tech: Feasible with LangGraph."
        assert result["findings"]["market"] == "Market: Growing at 40% CAGR."
        assert "Final Report:" in result["final_report"]
