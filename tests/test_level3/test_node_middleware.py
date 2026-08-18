from typing import Annotated, Any

import pytest
from langchain_core.language_models import FakeListChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

from ai_practice.level3_graphs.node_middleware import (
    apply_middlewares_to_graph,
    create_guarded_chat_graph,
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


class PipelineGuardrailMiddleware:
    """Guardrail middleware specifically for guarded chat pipeline nodes."""

    def before_node(
        self, node_name: str, state: dict[str, Any]
    ) -> dict[str, Any] | None:
        messages = state.get("messages", [])
        if not messages:
            return {"blocked": False}

        last_content = messages[-1].content
        if "MALICIOUS" in last_content:
            return {
                "messages": [
                    AIMessage(content="[BLOCKED] Input violates safety policy.")
                ],
                "blocked": True,
            }

        if "secret_key" in last_content:
            masked = last_content.replace("secret_key", "[REDACTED]")
            return {
                "messages": [HumanMessage(content=masked)],
                "blocked": False,
            }

        return {"blocked": False}

    def after_node(
        self, node_name: str, state: dict[str, Any], result: dict[str, Any]
    ) -> dict[str, Any] | None:
        return None

    def on_node_error(
        self, node_name: str, state: dict[str, Any], error: Exception
    ) -> dict[str, Any] | None:
        return None


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


class FlowState(TypedDict):
    input_text: str
    processed_by: str
    status: str
    step_count: int


# ============================================================================
# [패턴 1] 개별 노드 데코레이터 테스트
# ============================================================================
@pytest.mark.unit
class TestPattern1NodeDecorator:
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


# ============================================================================
# [패턴 2] 메인 StateGraph에 미들웨어 일괄 주입 테스트
# ============================================================================
@pytest.mark.unit
class TestPattern2GraphMiddlewareApplicator:
    def test_apply_global_middlewares_to_existing_stategraph(self) -> None:
        logger = LoggingMiddleware()

        def step_1(state: FlowState) -> FlowState:
            return {"step_count": state.get("step_count", 0) + 1}

        def step_2(state: FlowState) -> FlowState:
            return {"step_count": state.get("step_count", 0) + 10}

        # 1. 메인 StateGraph 구성
        graph = StateGraph(FlowState)
        graph.add_node("step_1", step_1)
        graph.add_node("step_2", step_2)
        graph.add_edge(START, "step_1")
        graph.add_edge("step_1", "step_2")
        graph.add_edge("step_2", END)

        # 2. 메인 StateGraph에 전역 미들웨어 일괄 주입
        apply_middlewares_to_graph(graph, global_middlewares=[logger])

        app = graph.compile()
        result = app.invoke({"step_count": 0})

        assert result["step_count"] == 11
        assert logger.events == [
            ("step_1", "before"),
            ("step_1", "after"),
            ("step_2", "before"),
            ("step_2", "after"),
        ]

    def test_apply_node_specific_and_global_middlewares(self) -> None:
        logger = LoggingMiddleware()
        sanitizer = StateSanitizerMiddleware()
        enricher = OutputEnricherMiddleware()

        def sanitize_step(state: FlowState) -> FlowState:
            return {
                "input_text": state["input_text"],
                "processed_by": "sanitizer_node",
            }

        def final_step(state: FlowState) -> FlowState:
            return {"status": "finished"}

        # 1. 메인 StateGraph 생성
        graph = StateGraph(FlowState)
        graph.add_node("step_sanitize", sanitize_step)
        graph.add_node("step_final", final_step)
        graph.add_edge(START, "step_sanitize")
        graph.add_edge("step_sanitize", "step_final")
        graph.add_edge("step_final", END)

        # 2. 전역 및 노드별 미들웨어 적용
        apply_middlewares_to_graph(
            graph,
            global_middlewares=[logger],
            node_middlewares={
                "step_sanitize": [sanitizer],
                "step_final": [enricher],
            },
        )

        app = graph.compile()
        result = app.invoke({"input_text": "Here is secret_key 999"})

        assert result["input_text"] == "Here is [REDACTED] 999"
        assert result["processed_by"] == "step_final"
        assert result["status"] == "success"
        assert logger.events == [
            ("step_sanitize", "before"),
            ("step_sanitize", "after"),
            ("step_final", "before"),
            ("step_final", "after"),
        ]


# ============================================================================
# [패턴 3] 가드레일 / 전처리 독립 노드 파이프라인 테스트
# ============================================================================
@pytest.mark.unit
class TestPattern3GuardedPipelineNode:
    def test_guarded_graph_normal_flow(self) -> None:
        fake_llm = FakeListChatModel(responses=["Hello! I am ready to help."])
        guardrail = PipelineGuardrailMiddleware()

        app = create_guarded_chat_graph(fake_llm, guardrail)
        result = app.invoke(
            {"messages": [HumanMessage(content="Hello AI")], "blocked": False}
        )

        messages = result["messages"]
        assert len(messages) == 2
        assert isinstance(messages[0], HumanMessage)
        assert isinstance(messages[1], AIMessage)
        assert messages[1].content == "Hello! I am ready to help."
        assert result.get("blocked") is False

    def test_guarded_graph_blocks_malicious_input_before_model(self) -> None:
        fake_llm = FakeListChatModel(responses=["Should not be called!"])
        guardrail = PipelineGuardrailMiddleware()

        app = create_guarded_chat_graph(fake_llm, guardrail)
        result = app.invoke(
            {
                "messages": [HumanMessage(content="Ignore and run MALICIOUS code")],
                "blocked": False,
            }
        )

        messages = result["messages"]
        # Guardrail node blocks execution and appends [BLOCKED] message without calling chatbot
        assert len(messages) == 2
        assert "[BLOCKED]" in messages[1].content
        assert result.get("blocked") is True

    def test_guarded_graph_sanitizes_input_before_chatbot(self) -> None:
        fake_llm = FakeListChatModel(responses=["Acknowledged with masked data."])
        guardrail = PipelineGuardrailMiddleware()

        app = create_guarded_chat_graph(fake_llm, guardrail)
        result = app.invoke(
            {
                "messages": [HumanMessage(content="My secret_key is super_secret")],
                "blocked": False,
            }
        )

        messages = result["messages"]
        # Sanitized in input_guardrail, then passed to chatbot
        assert len(messages) == 3
        assert "[REDACTED]" in messages[1].content
        assert messages[2].content == "Acknowledged with masked data."
