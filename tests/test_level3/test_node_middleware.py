from typing import Annotated, Any

import pytest
from langchain_core.language_models import FakeListChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from ai_practice.level3_graphs.node_middleware import (
    wrap_node_with_middleware,
)


class LoggingMiddleware:
    """Records before/after execution events for debugging and auditing."""

    def __init__(self) -> None:
        self.events: list[tuple[str, str]] = []

    def before_node(
        self, node_name: str, state: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.events.append((node_name, "before"))
        return None

    def after_node(
        self, node_name: str, state: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any] | None:
        self.events.append((node_name, "after"))
        return None

    def on_node_error(
        self, node_name: str, state: dict[str, Any], error: Exception
    ) -> dict[str, Any] | None:
        self.events.append((node_name, f"error: {type(error).__name__}"))
        return None


class StateSanitizerMiddleware:
    """Sanitizes or enriches state before node execution."""

    def before_node(
        self, node_name: str, state: dict[str, Any]
    ) -> dict[str, Any] | None:
        raw_text = state.get("input_text", "")
        # Mask sensitive word 'secret_key'
        sanitized = raw_text.replace("secret_key", "[REDACTED]")
        return {"input_text": sanitized, "sanitized": True}

    def after_node(
        self, node_name: str, state: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any] | None:
        return None

    def on_node_error(
        self, node_name: str, state: dict[str, Any], error: Exception
    ) -> dict[str, Any] | None:
        return None


class OutputEnricherMiddleware:
    """Appends metadata or transforms node output."""

    def before_node(
        self, node_name: str, state: dict[str, Any]
    ) -> dict[str, Any] | None:
        return None

    def after_node(
        self, node_name: str, state: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any] | None:
        return {"status": "success", "processed_by": node_name}

    def on_node_error(
        self, node_name: str, state: dict[str, Any], error: Exception
    ) -> dict[str, Any] | None:
        return None


class SecurityGuardMiddleware:
    """Blocks execution if forbidden input pattern is found."""

    def before_node(
        self, node_name: str, state: dict[str, Any]
    ) -> dict[str, Any] | None:
        if "MALICIOUS" in state.get("input_text", ""):
            raise PermissionError("Access denied by security middleware")
        return None

    def after_node(
        self, node_name: str, state: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any] | None:
        return None

    def on_node_error(
        self, node_name: str, state: dict[str, Any], error: Exception
    ) -> dict[str, Any] | None:
        return None


class FallbackRecoveryMiddleware:
    """Catches exceptions and returns fallback response."""

    def before_node(
        self, node_name: str, state: dict[str, Any]
    ) -> dict[str, Any] | None:
        return None

    def after_node(
        self, node_name: str, state: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any] | None:
        return None

    def on_node_error(
        self, node_name: str, state: dict[str, Any], error: Exception
    ) -> dict[str, Any] | None:
        return {"messages": [AIMessage(content="Service temporarily degraded.")]}


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


@pytest.mark.unit
class TestNodeMiddleware:
    def test_logging_middleware_tracks_execution_order(self) -> None:
        mw = LoggingMiddleware()

        def sample_node(state: dict[str, Any]) -> dict[str, Any]:
            return {"output": state["value"] * 2}

        wrapped = wrap_node_with_middleware("sample", sample_node, [mw])
        result = wrapped({"value": 10})

        assert result == {"output": 20}
        assert mw.events == [("sample", "before"), ("sample", "after")]

    def test_middleware_state_transformation(self) -> None:
        sanitizer = StateSanitizerMiddleware()

        def echo_node(state: dict[str, Any]) -> dict[str, Any]:
            return {"result": f"Received: {state['input_text']}"}

        wrapped = wrap_node_with_middleware("echo", echo_node, [sanitizer])
        output = wrapped({"input_text": "My secret_key is 1234"})

        assert output == {"result": "Received: My [REDACTED] is 1234"}

    def test_middleware_output_transformation(self) -> None:
        enricher = OutputEnricherMiddleware()

        def basic_node(state: dict[str, Any]) -> dict[str, Any]:
            return {"data": 42}

        wrapped = wrap_node_with_middleware("worker", basic_node, [enricher])
        output = wrapped({"data": 0})

        assert output == {"data": 42, "status": "success", "processed_by": "worker"}

    def test_middleware_blocks_execution_on_security_error(self) -> None:
        security = SecurityGuardMiddleware()
        node_called = False

        def dangerous_node(state: dict[str, Any]) -> dict[str, Any]:
            nonlocal node_called
            node_called = True
            return {"status": "ok"}

        wrapped = wrap_node_with_middleware("danger", dangerous_node, [security])

        with pytest.raises(
            PermissionError, match="Access denied by security middleware"
        ):
            wrapped({"input_text": "MALICIOUS payload"})

        assert not node_called

    def test_middleware_error_recovery(self) -> None:
        logger = LoggingMiddleware()
        recovery = FallbackRecoveryMiddleware()

        def failing_node(state: dict[str, Any]) -> dict[str, Any]:
            raise TimeoutError("Connection to LLM provider timed out")

        wrapped = wrap_node_with_middleware(
            "llm_node", failing_node, [logger, recovery]
        )
        result = wrapped({"messages": [HumanMessage(content="Hello")]})

        # Should catch error and return fallback
        assert "messages" in result
        assert result["messages"][0].content == "Service temporarily degraded."
        assert logger.events == [
            ("llm_node", "before"),
            ("llm_node", "error: TimeoutError"),
        ]

    def test_middleware_in_compiled_stategraph(self) -> None:
        logger = LoggingMiddleware()
        fake_llm = FakeListChatModel(responses=["Hello, world!"])

        def chatbot_node(state: ChatState) -> ChatState:
            response = fake_llm.invoke(state["messages"])
            return {"messages": [response]}

        # Wrap chatbot_node with LoggingMiddleware
        wrapped_chatbot = wrap_node_with_middleware("chatbot", chatbot_node, [logger])

        graph = StateGraph(ChatState)
        graph.add_node("chatbot", wrapped_chatbot)
        graph.add_edge(START, "chatbot")
        graph.add_edge("chatbot", END)

        app = graph.compile()
        res = app.invoke({"messages": [HumanMessage(content="Hi")]})

        assert len(res["messages"]) == 2
        assert res["messages"][1].content == "Hello, world!"
        assert logger.events == [("chatbot", "before"), ("chatbot", "after")]
