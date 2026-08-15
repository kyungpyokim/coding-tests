import re


class GuardrailError(Exception):
    """Raised when an input or output violates AI safety guardrails."""


EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_PATTERN = re.compile(r"\b(?:\d{2,3}[-.\s]?)?\d{3,4}[-.\s]?\d{4}\b")

INJECTION_PATTERNS = [
    r"ignore (?:all )?previous instructions",
    r"reveal (?:the )?system prompt",
    r"bypass safety (?:filter|guard)",
    r"you are now (?:dan|unrestricted)",
    r"dump (?:the )?database",
]


def mask_pii(text: str) -> str:
    """Mask Personally Identifiable Information (PII) such as emails and phone numbers."""
    masked = EMAIL_PATTERN.sub("[EMAIL_MASKED]", text)
    masked = PHONE_PATTERN.sub("[PHONE_MASKED]", masked)
    return masked


def detect_prompt_injection(text: str) -> bool:
    """Detect common prompt injection and jailbreak patterns."""
    text_lower = text.lower()
    return any(re.search(pattern, text_lower) for pattern in INJECTION_PATTERNS)


def validate_and_sanitize_input(text: str) -> str:
    """Validate input against prompt injection and mask PII."""
    if detect_prompt_injection(text):
        raise GuardrailError("Prompt injection detected in input.")
    return mask_pii(text)
