import pytest
from pydantic import BaseModel, Field

from ai_practice.level1_basics.structured_parser import (
    ParsingError,
    extract_json_string,
    parse_to_model,
)


class UserProfile(BaseModel):
    name: str
    age: int
    interests: list[str] = Field(default_factory=list)


@pytest.mark.unit
class TestExtractJsonString:
    def test_extract_from_plain_json(self):
        raw = '{"name": "Alice", "age": 30}'
        assert extract_json_string(raw) == '{"name": "Alice", "age": 30}'

    def test_extract_from_markdown_block(self):
        raw = """Here is the result:
```json
{
  "name": "Bob",
  "age": 25
}
```
Hope that helps!"""
        expected = '{\n  "name": "Bob",\n  "age": 25\n}'
        assert extract_json_string(raw) == expected

    def test_extract_from_generic_markdown_block(self):
        raw = """```
{"name": "Charlie", "age": 40}
```"""
        assert extract_json_string(raw) == '{"name": "Charlie", "age": 40}'

    def test_extract_when_no_json_found_raises_error(self):
        raw = "There is no json object here at all."
        with pytest.raises(ParsingError, match="No valid JSON found"):
            extract_json_string(raw)


@pytest.mark.unit
class TestParseToModel:
    def test_parse_valid_json_into_pydantic_model(self):
        raw = '```json\n{"name": "Dave", "age": 28, "interests": ["coding", "ai"]}\n```'
        profile = parse_to_model(raw, UserProfile)
        assert isinstance(profile, UserProfile)
        assert profile.name == "Dave"
        assert profile.age == 28
        assert profile.interests == ["coding", "ai"]

    def test_parse_with_missing_required_field_raises_error(self):
        raw = '{"name": "Eve"}'  # missing 'age'
        with pytest.raises(ParsingError, match="Validation failed"):
            parse_to_model(raw, UserProfile)

    def test_parse_malformed_json_raises_error(self):
        raw = '```json\n{"name": "Frank", "age": }\n```'
        with pytest.raises(ParsingError, match="Malformed JSON"):
            parse_to_model(raw, UserProfile)
