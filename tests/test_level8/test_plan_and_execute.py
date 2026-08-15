import pytest

from ai_practice.level8_planner.plan_and_execute import (
    create_plan_and_execute_agent,
)


@pytest.mark.unit
class TestPlanAndExecute:
    def test_plan_and_execute_workflow(self):
        # 1. Planner generates 2 steps
        def mock_planner(goal: str) -> list[str]:
            return ["Step 1: Fetch GDP data", "Step 2: Calculate growth rate"]

        # 2. Executor executes step
        def mock_executor(step: str) -> str:
            if "GDP" in step:
                return "GDP is $10T"
            return "Growth rate is 5%"

        # 3. Replanner checks if steps remain
        def mock_replanner(
            goal: str,
            remaining_plan: list[str],
            past_steps: list[tuple[str, str]],
        ) -> tuple[list[str], str | None]:
            if not remaining_plan:
                summary = "Final: " + ", ".join(f"{res}" for _, res in past_steps)
                return [], summary
            return remaining_plan, None

        agent = create_plan_and_execute_agent(
            mock_planner, mock_executor, mock_replanner
        )
        result = agent.invoke(
            {
                "input": "Analyze GDP growth",
                "plan": [],
                "past_steps": [],
                "response": None,
            }
        )

        assert len(result["past_steps"]) == 2
        assert result["past_steps"][0] == (
            "Step 1: Fetch GDP data",
            "GDP is $10T",
        )
        assert result["past_steps"][1] == (
            "Step 2: Calculate growth rate",
            "Growth rate is 5%",
        )
        assert result["response"] == "Final: GDP is $10T, Growth rate is 5%"
