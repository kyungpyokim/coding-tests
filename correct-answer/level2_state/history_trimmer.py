import math

from langchain_core.messages import BaseMessage, SystemMessage


def estimate_tokens(text: str) -> int:
    """Estimate token count for a given text string (approx 4 chars per token)."""
    if not text:
        return 0
    return math.ceil(len(text) / 4)


def trim_messages(
    messages: list[BaseMessage], max_tokens: int, preserve_system: bool = True
) -> list[BaseMessage]:
    """Trim older conversation messages to fit within a max token budget.

    If preserve_system is True, SystemMessage at index 0 should always be kept.
    """
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
