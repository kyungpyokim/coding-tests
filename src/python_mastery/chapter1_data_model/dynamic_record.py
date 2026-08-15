from collections.abc import Iterator, Mapping
from typing import Any


class DynamicRecord:
    """A hybrid record supporting both attribute (dot) and mapping (dict) access.

    Demonstrates Python's Attribute & Mapping Protocols:
    - Attribute Interception: __getattr__, __setattr__, __delattr__
    - Item Access: __getitem__, __setitem__, __delitem__
    - Container Protocol: __len__, __iter__, __contains__
    - Deep conversion: Nested dicts become DynamicRecords recursively.
    """

    def __init__(self, data: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        """Initialize DynamicRecord.

        Attributes should be stored in an internal `_data` dict.
        Nested dicts must be recursively converted to DynamicRecords.
        """
        # Note: 내부 _data 저장을 위해 object.__setattr__을 사용하는 것이 안전합니다.
        object.__setattr__(self, "_data", {})
        # TODO: data 및 kwargs의 모든 키-값 쌍을 저장하세요.
        # 값이 dict(Mapping)인 경우 DynamicRecord로 재귀 변환하세요.
        raise NotImplementedError

    def __getattr__(self, name: str) -> Any:
        """Access attribute via dot notation: record.key."""
        # TODO: name이 _data에 있으면 반환하고, 없으면 AttributeError를 발생시키세요.
        raise NotImplementedError

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute via dot notation: record.key = value."""
        # TODO: _data가 초기화되지 않았거나 name이 private('_' 시작)인 경우 object.__setattr__을 호출하고,
        # 일반 속성은 value가 dict면 DynamicRecord로 감싸서 _data[name]에 저장하세요.
        raise NotImplementedError

    def __delattr__(self, name: str) -> None:
        """Delete attribute via dot notation: del record.key."""
        # TODO: _data에서 name을 삭제하세요. 없으면 AttributeError를 발생시키세요.
        raise NotImplementedError

    def __getitem__(self, key: str) -> Any:
        """Access item via dictionary notation: record['key']."""
        # TODO: _data[key]를 반환하세요. 없으면 KeyError가 발생합니다.
        raise NotImplementedError

    def __setitem__(self, key: str, value: Any) -> None:
        """Set item via dictionary notation: record['key'] = value."""
        # TODO: value가 dict면 DynamicRecord로 감싸서 _data[key]에 저장하세요.
        raise NotImplementedError

    def __delitem__(self, key: str) -> None:
        """Delete item via dictionary notation: del record['key']."""
        # TODO: _data에서 key를 삭제하세요.
        raise NotImplementedError

    def __contains__(self, key: Any) -> bool:
        """Support `key in record`."""
        # TODO: key가 _data에 존재하는지 반환하세요.
        raise NotImplementedError

    def __len__(self) -> int:
        """Return the number of stored keys."""
        # TODO: _data의 키 개수를 반환하세요.
        raise NotImplementedError

    def __iter__(self) -> Iterator[str]:
        """Iterate over keys."""
        # TODO: _data의 키 이터레이터를 반환하세요.
        raise NotImplementedError

    def to_dict(self) -> dict[str, Any]:
        """Recursively export the record back to a plain Python dict."""
        # TODO: 중첩된 DynamicRecord들을 모두 일반 dict로 변환하여 순수 dict를 반환하세요.
        raise NotImplementedError

    def __repr__(self) -> str:
        """Return a readable representation: DynamicRecord({'a': 1})."""
        # TODO: DynamicRecord(내부데이터) 형태의 문자열을 반환하세요.
        raise NotImplementedError
