import math
import time
from typing import Any

from pydantic import BaseModel, Field


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """Calculate cosine similarity between two float vectors."""
    dot = sum(a * b for a, b in zip(vec_a, vec_b, strict=False))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


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
        expires_at = time.time() + ttl_seconds if ttl_seconds is not None else None
        entry = CacheEntry(
            query=query,
            embedding=embedding,
            response=response,
            expires_at=expires_at,
        )
        self.entries.append(entry)

    def get(
        self, query_embedding: list[float], similarity_threshold: float = 0.85
    ) -> str | None:
        """Retrieve cached response if cosine similarity >= similarity_threshold."""
        now = time.time()
        best_score = -1.0
        best_response: str | None = None

        for entry in self.entries:
            # Check expiration
            if entry.expires_at is not None and now > entry.expires_at:
                continue

            score = cosine_similarity(query_embedding, entry.embedding)
            if score >= similarity_threshold and score > best_score:
                best_score = score
                best_response = entry.response

        return best_response

    def cleanup_expired(self) -> int:
        """Evict all expired cache entries and return count of removed items."""
        now = time.time()
        initial_len = len(self.entries)
        self.entries = [
            e for e in self.entries if e.expires_at is None or now <= e.expires_at
        ]
        return initial_len - len(self.entries)
