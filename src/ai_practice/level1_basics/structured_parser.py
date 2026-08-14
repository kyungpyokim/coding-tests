from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class ParsingError(Exception):
    """Raised when JSON extraction or Pydantic validation fails."""


def extract_json_string(text: str) -> str:
    """Extract a JSON string from plain text or markdown code blocks."""
    # TODO: 마크다운 코드블록(```json ... ```) 또는 일반 텍스트에서 JSON 객체({...}) 문자열을 추출하세요.
    # JSON을 찾을 수 없으면 ParsingError를 발생시키세요.
    raise NotImplementedError


def parse_to_model(text: str, model_cls: type[T]) -> T:
    """Extract and validate JSON into a Pydantic model."""
    # TODO: extract_json_string을 사용해 JSON을 추출하고, model_cls로 검증(validate)하여 반환하세요.
    # JSON 디코딩 실패나 ValidationError 발생 시 ParsingError로 감싸서 발생시키세요.
    raise NotImplementedError
