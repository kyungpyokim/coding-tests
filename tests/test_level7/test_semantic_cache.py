import time

import pytest

from ai_practice.level7_caching.semantic_cache import (
    SemanticCache,
    cosine_similarity,
)


@pytest.mark.unit
class TestSemanticCache:
    def test_cosine_similarity(self):
        v1 = [1.0, 0.0]
        v2 = [1.0, 0.0]
        v3 = [0.0, 1.0]
        assert cosine_similarity(v1, v2) == pytest.approx(1.0)
        assert cosine_similarity(v1, v3) == pytest.approx(0.0)

    def test_cache_hit_on_similar_embedding(self):
        cache = SemanticCache()
        # Query: "How to parse json in python?"
        cache.set(
            query="How to parse json in python?",
            embedding=[0.9, 0.1],
            response="Use `json.loads(text)`.",
        )

        # Similar Query: "Parse json python example" -> [0.88, 0.12]
        cached_resp = cache.get(query_embedding=[0.88, 0.12], similarity_threshold=0.9)
        assert cached_resp == "Use `json.loads(text)`."

    def test_cache_miss_on_dissimilar_embedding(self):
        cache = SemanticCache()
        cache.set(
            query="How to parse json in python?",
            embedding=[1.0, 0.0],
            response="Use `json.loads(text)`.",
        )

        # Dissimilar query: "How to cook noodles" -> [0.0, 1.0]
        cached_resp = cache.get(query_embedding=[0.0, 1.0], similarity_threshold=0.85)
        assert cached_resp is None

    def test_cache_ttl_and_cleanup(self):
        cache = SemanticCache()
        cache.set(
            query="Short lived query",
            embedding=[1.0, 0.0],
            response="Temporary answer",
            ttl_seconds=0.01,
        )

        # Wait for expiration
        time.sleep(0.02)

        # Should be a miss due to expiration
        assert cache.get([1.0, 0.0]) is None

        # Cleanup should remove the expired item
        removed_count = cache.cleanup_expired()
        assert removed_count == 1
        assert len(cache.entries) == 0
