import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ParsingError(Exception):
    """Raised when JSON extraction or Pydantic validation fails."""


def extract_json_string(text: str) -> str:
    """Extract a JSON string from plain text or markdown code blocks."""
    # 1. 마크다운 코드 블록 확인 (```json ... ``` 또는 ``` ... ```)
    code_block_match = re.search(r"```(?:json)?\s*\n?([\s\S]*?)\n?```", text)
    if code_block_match:
        return code_block_match.group(1).strip()

    # 2. 일반 텍스트에서 { ... } 형태의 JSON 객체 추출
    json_match = re.search(r"\{[\s\S]*\}", text)
    if json_match:
        return json_match.group(0).strip()

    raise ParsingError("No valid JSON found")


def parse_to_model(text: str, model_cls: type[T]) -> T:
    """Extract and validate JSON into a Pydantic model."""
    json_string = extract_json_string(text)
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError as e:
        raise ParsingError("Malformed JSON") from e

    try:
        return model_cls.model_validate(data)
    except ValidationError as e:
        raise ParsingError("Validation failed") from e
