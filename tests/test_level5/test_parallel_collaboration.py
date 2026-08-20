from typing import Any

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from ai_practice.level5_multi_agent.parallel_collaboration import (
    ParallelCollaborationState,
    create_aggregator_node,
    create_parallel_collaboration_system,
    create_worker_node,
)


class MockLLM:
    def __init__(self, responses: list[str] | dict[str, str] | None = None) -> None:
        self.calls: list[Any] = []
        if isinstance(responses, dict):
            self.response_map = responses
            self.responses: list[str] = []
        else:
            self.response_map = {}
            self.responses = list(responses or [])

    def invoke(self, messages: Any, **kwargs: Any) -> AIMessage:
        self.calls.append(messages)
        content_str = ""
        if isinstance(messages, list) and messages:
            content_str = getattr(messages[0], "content", str(messages[0]))
        elif isinstance(messages, str):
            content_str = messages
        else:
            content_str = str(messages)

        if self.response_map:
            for key, val in self.response_map.items():
                if key.lower() in content_str.lower():
                    return AIMessage(content=val)

        if self.responses:
            return AIMessage(content=self.responses.pop(0))
        return AIMessage(content="Default mock output")


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

        # 결과 검증
        assert result == {"findings": {"tech": "Technical feasibility is high."}}
        # 프롬프트 및 HumanMessage 호출 규격 검증
        assert len(model.calls) == 1
        call_msg = model.calls[0]
        assert isinstance(call_msg, list)
        assert isinstance(call_msg[0], HumanMessage)
        assert call_msg[0].content == "Analyze the following topic from a tech perspective: AI Automation"

    def test_worker_node_empty_topic_edge_case(self):
        model = MockLLM(["Should not be called"])
        worker = create_worker_node(model, "tech")

        state: ParallelCollaborationState = {
            "topic": "   ",
            "findings": {},
            "final_report": "",
        }
        result = worker(state)

        assert result == {"findings": {"tech": "No topic provided for tech."}}
        assert len(model.calls) == 0  # LLM이 호출되지 않아야 함

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
        assert len(model.calls) == 1
        call_msg = model.calls[0]
        assert isinstance(call_msg, list)
        assert isinstance(call_msg[0], HumanMessage)
        assert "Synthesize these domain findings for 'AI Automation' into a final report:" in call_msg[0].content
        assert "- [tech]: Technical feasibility is high." in call_msg[0].content
        assert "- [finance]: Initial investment 10k, ROI expected in 6 months." in call_msg[0].content

    def test_aggregator_node_empty_findings_edge_case(self):
        model = MockLLM(["Should not be called"])
        aggregator = create_aggregator_node(model)

        state: ParallelCollaborationState = {
            "topic": "AI Automation",
            "findings": {},
            "final_report": "",
        }
        result = aggregator(state)

        assert result == {"final_report": "No findings available to aggregate."}
        assert len(model.calls) == 0  # LLM이 호출되지 않아야 함

    def test_parallel_collaboration_fan_out_fan_in(self):
        # 2 workers + 1 aggregator (키워드 매핑으로 병렬 순서에 독립적 검증)
        model = MockLLM({
            "tech perspective": "Tech: Feasible with LangGraph.",
            "market perspective": "Market: Growing at 40% CAGR.",
            "Synthesize": "Final Report: Strong market demand with solid tech foundations.",
        })

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
        assert result["final_report"] == "Final Report: Strong market demand with solid tech foundations."

    def test_system_empty_domains_raises_error(self):
        model = MockLLM()
        with pytest.raises(ValueError, match="domains must not be empty"):
            create_parallel_collaboration_system(model, [])

    def test_system_duplicate_domains_raises_error(self):
        model = MockLLM()
        with pytest.raises(ValueError, match="domains must be unique"):
            create_parallel_collaboration_system(model, ["tech", "tech"])

    def test_system_single_domain(self):
        model = MockLLM({
            "tech perspective": "Tech: All good.",
            "Synthesize": "Final: Looks solid.",
        })
        system = create_parallel_collaboration_system(model, ["tech"])
        result = system.invoke({
            "topic": "Single domain test",
            "findings": {},
            "final_report": "",
        })

        assert result["findings"] == {"tech": "Tech: All good."}
        assert result["final_report"] == "Final: Looks solid."
