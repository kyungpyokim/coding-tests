from collections.abc import Callable

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
        [str, list[str], list[tuple[str, str]]], tuple[list[str], str | None]
    ],
) -> CompiledStateGraph:
    """Build a Plan-and-Execute StateGraph.

    Workflow:
    1. Node 'planner': Runs planner_fn(input) to populate state['plan'].
    2. Node 'executor': Takes the first step in state['plan'], executes via executor_fn(step),
       appends (step, result) to state['past_steps'], and removes the step from state['plan'].
    3. Node 'replan': Calls replanner_fn(input, plan, past_steps) to decide:
       - Remaining steps (new plan)
       - Final response (if finished)
    4. Conditional Edge after 'replan':
       - If response is present -> END
       - Else if plan is not empty -> loop back to 'executor'
       - Else -> END
    """
    # TODO: StateGraph(PlanExecuteState)를 생성하고 planner, executor, replanner 노드 및 엣지를 연결하세요.
    raise NotImplementedError
