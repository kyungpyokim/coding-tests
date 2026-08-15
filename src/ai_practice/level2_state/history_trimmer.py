import math

from langchain_core.messages import BaseMessage, SystemMessage


def estimate_tokens(text: str) -> int:
    """Estimate token count for a given text string (approx 4 chars per token)."""
    # TODO: 대략적인 토큰 수를 계산하여 반환하세요 (공백/글자 기준, 올림 계산 등).
    n = len(text) / 4

    return math.ceil(n)


def trim_messages(
    messages: list[BaseMessage], max_tokens: int, preserve_system: bool = True
) -> list[BaseMessage]:
    """Trim older conversation messages to fit within a max token budget.

    If preserve_system is True, SystemMessage at index 0 should always be kept.
    """
    # TODO: 최신 메시지부터 역순으로 탐색하여 max_tokens 한도 내의 메시지만 남기고,
    # preserve_system이 True인 경우 첫 번째 SystemMessage를 항상 맨 앞에 유지하세요.
    if not messages:
        return []

    system_msg: BaseMessage | None = None
    remaining_messages = messages

    if preserve_system and isinstance(messages[0], SystemMessage):
        system_msg = messages[0]
        remaining_messages = messages[1:]
        max_tokens -= estimate_tokens(str(system_msg.content))

    kept_reversed: list[BaseMessage] = []
    current_tokens = 0

    for msg in reversed(remaining_messages):
        msg_tokens = estimate_tokens(str(msg.content))
        if current_tokens + msg_tokens <= max_tokens:
            kept_reversed.append(msg)
            current_tokens += msg_tokens
        else:
            break

    kept = list(reversed(kept_reversed))
    if system_msg is not None:
        return [system_msg, *kept]
    return kept
