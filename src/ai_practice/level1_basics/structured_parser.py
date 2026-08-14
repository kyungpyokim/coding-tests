import json
import re
from typing import TypeVar

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound=BaseModel)


class ParsingError(Exception):
    """Raised when JSON extraction or Pydantic validation fails."""


def extract_json_string(text: str) -> str:
    """Extract a JSON string from plain text or markdown code blocks."""
    # Check for markdown code blocks (e.g. ```json ... ``` or ``` ... ```)
    code_block_pattern = r"```(?:json)?\s*\n?([\s\S]*?)\n?```"
    match = re.search(code_block_pattern, text.strip())
    if match:
        extracted = match.group(1).strip()
        if extracted.startswith("{") and extracted.endswith("}"):
            return extracted

    # Check for standalone JSON object
    json_object_pattern = r"\{[\s\S]*\}"
    match = re.search(json_object_pattern, text.strip())
    if match:
        return match.group(0).strip()

    raise ParsingError("No valid JSON found in response.")


def parse_to_model(text: str, model_cls: type[T]) -> T:
    """Extract and validate JSON into a Pydantic model."""
    json_str = extract_json_string(text)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as err:
        raise ParsingError(f"Malformed JSON: {err}") from err

    try:
        return model_cls.model_validate(data)
    except ValidationError as err:
        raise ParsingError(
            f"Validation failed for {model_cls.__name__}: {err}"
        ) from err
