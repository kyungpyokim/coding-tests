import pytest
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from ai_practice.level12_distributed_state.time_travel import (
    build_time_travel_graph,
    get_state_history,
    rollback_and_branch,
)


@pytest.mark.unit
class TestTimeTravel:
    def test_state_history_tracking(self):
        checkpointer = MemorySaver()
        graph = build_time_travel_graph(checkpointer)
        config = {"configurable": {"thread_id": "thread_debug_1"}}

        # Turn 1
        graph.invoke(
            {"messages": [HumanMessage(content="Turn 1")], "step_count": 0},
            config=config,
        )
        # Turn 2
        graph.invoke({"messages": [HumanMessage(content="Turn 2")]}, config=config)

        history = get_state_history(graph, thread_id="thread_debug_1")
        # Should have multiple snapshots
        assert len(history) >= 2
        assert all("checkpoint_id" in snap for snap in history)
        assert all("values" in snap for snap in history)

    def test_rollback_and_branch_fork(self):
        checkpointer = MemorySaver()
        graph = build_time_travel_graph(checkpointer)
        config = {"configurable": {"thread_id": "thread_fork_1"}}

        # Step 1: Initial question
        graph.invoke(
            {
                "messages": [HumanMessage(content="Question A")],
                "step_count": 0,
            },
            config=config,
        )
        # Step 2: Follow-up question
        graph.invoke(
            {"messages": [HumanMessage(content="Follow-up B")]},
            config=config,
        )

        history = get_state_history(graph, thread_id="thread_fork_1")
        # Oldest checkpoint after Turn 1
        turn1_checkpoint = history[-2]["checkpoint_id"]

        # Branch off from Turn 1 with alternative Question C
        branched_messages = rollback_and_branch(
            graph,
            thread_id="thread_fork_1",
            target_checkpoint_id=turn1_checkpoint,
            new_message=HumanMessage(content="Alternative Question C"),
        )

        # The new branch should contain Question A and Question C, NOT Follow-up B
        contents = [m.content for m in branched_messages]
        assert "Question A" in contents
        assert "Alternative Question C" in contents
        assert "Follow-up B" not in contents
