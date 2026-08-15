from collections.abc import Callable
from typing import Any

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class Plan(BaseModel):
    """Step-by-step plan for solving a complex goal."""

    steps: list[str] = Field(description="List of sequential steps to execute")


class PlanExecuteState(TypedDict):
    """State for Plan-and-Execute workflow."""

    input: str
    plan: list[str]
    past_steps: list[tuple[str, str]]
    response: str | None


def create_plan_and_execute_agent(
    planner_fn: Callable[[str], list[str]],
    executor_fn: Callable[[str], str],
    replanner_fn: Callable[
        [str, list[str], list[tuple[str, str]]],
        tuple[list[str], str | None],
    ],
) -> CompiledStateGraph:
    """Build a Plan-and-Execute StateGraph."""
    builder = StateGraph(PlanExecuteState)

    def planner_node(state: PlanExecuteState) -> dict[str, Any]:
        plan = planner_fn(state["input"])
        return {"plan": plan, "past_steps": [], "response": None}

    def executor_node(state: PlanExecuteState) -> dict[str, Any]:
        plan = list(state["plan"])
        current_step = plan.pop(0)
        result = executor_fn(current_step)
        past_steps = list(state["past_steps"]) + [(current_step, result)]
        return {"plan": plan, "past_steps": past_steps}

    def replanner_node(state: PlanExecuteState) -> dict[str, Any]:
        new_plan, response = replanner_fn(
            state["input"], state["plan"], state["past_steps"]
        )
        return {"plan": new_plan, "response": response}

    def should_continue(state: PlanExecuteState) -> str:
        if state.get("response") is not None:
            return END
        if state.get("plan"):
            return "executor"
        return END

    builder.add_node("planner", planner_node)
    builder.add_node("executor", executor_node)
    builder.add_node("replan", replanner_node)

    builder.add_edge(START, "planner")
    builder.add_edge("planner", "executor")
    builder.add_edge("executor", "replan")
    builder.add_conditional_edges(
        "replan",
        should_continue,
        {"executor": "executor", END: END},
    )

    return builder.compile()
