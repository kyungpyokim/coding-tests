class GuardrailError(Exception):
    """Raised when an input or output violates AI safety guardrails."""


def mask_pii(text: str) -> str:
    """Mask Personally Identifiable Information (PII) such as emails and phone numbers.

    - Email: 'user@example.com' -> '[EMAIL_MASKED]'
    - Phone: '010-1234-5678' -> '[PHONE_MASKED]'
    """
    # TODO: 정규식을 활용하여 이메일과 전화번호를 안전하게 마스킹하세요.
    raise NotImplementedError


def detect_prompt_injection(text: str) -> bool:
    """Detect common prompt injection and jailbreak patterns.

    Detect patterns like:
    - 'ignore previous instructions'
    - 'system prompt reveal'
    - 'bypass safety filter'
    - 'you are now DAN' / 'unrestricted mode'
    """
    # TODO: 프롬프트 인젝션 의도가 담긴 키워드나 패턴을 탐지하여 True/False를 반환하세요.
    raise NotImplementedError


def validate_and_sanitize_input(text: str) -> str:
    """Validate input against prompt injection and mask PII.

    Raises GuardrailError if prompt injection is detected.
    Returns sanitized text with PII masked.
    """
    # TODO: 인젝션 탐지 시 GuardrailError를 발생시키고, 정상이면 PII를 마스킹하여 반환하세요.
    raise NotImplementedError
