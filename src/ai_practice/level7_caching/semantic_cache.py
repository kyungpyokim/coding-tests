from typing import Any

from pydantic import BaseModel, Field


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Calculate cosine similarity between two float vectors."""
    # TODO: 두 벡터 간의 코사인 유사도를 계산하세요 (-1.0 ~ 1.0).
    raise NotImplementedError


class CacheEntry(BaseModel):
    query: str
    embedding: list[float]
    response: str
    expires_at: float | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class SemanticCache:
    """Embedding-based semantic cache with similarity threshold and TTL eviction."""

    def __init__(self) -> None:
        self.entries: list[CacheEntry] = []

    def set(
        self,
        query: str,
        embedding: list[float],
        response: str,
        ttl_seconds: float | None = None,
    ) -> None:
        """Store query, embedding, and response in cache with optional TTL."""
        # TODO: 캐시 엔트리를 생성하고 현재 시간 + ttl_seconds 만료 시점을 기록하여 저장하세요.
        raise NotImplementedError

    def get(
        self, query_embedding: list[float], similarity_threshold: float = 0.85
    ) -> str | None:
        """Retrieve cached response if cosine similarity >= similarity_threshold."""
        # TODO: 만료되지 않은 캐시 중 유사도가 가장 높고 threshold 이상인 응답을 반환하세요. 없으면 None 반환.
        raise NotImplementedError

    def cleanup_expired(self) -> int:
        """Evict all expired cache entries and return count of removed items."""
        # TODO: 현재 시간 기준으로 만료된 항목들을 캐시에서 삭제하고 제거된 개수를 반환하세요.
        raise NotImplementedError
