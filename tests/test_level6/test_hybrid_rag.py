import pytest

from ai_practice.level6_rag.hybrid_rag import (
    Document,
    InMemoryVectorStore,
    reciprocal_rank_fusion,
    recursive_character_chunk,
)


@pytest.mark.unit
class TestHybridRag:
    def test_recursive_character_chunk(self):
        text = "1234567890abcdefghij"  # 20 chars
        # chunk_size=10, overlap=2 -> chunk 1: 0..10, chunk 2: 8..18, chunk 3: 16..20
        chunks = recursive_character_chunk(text, chunk_size=10, overlap=2)
        assert len(chunks) == 3
        assert chunks[0] == "1234567890"
        assert chunks[1] == "90abcdefgh"
        assert chunks[2] == "ghij"

    def test_vector_store_similarity_search(self):
        store = InMemoryVectorStore()
        docs = [
            Document(id="doc_ai", content="Artificial Intelligence and Agents"),
            Document(id="doc_cook", content="Cooking pasta recipes"),
            Document(id="doc_ml", content="Machine Learning basics"),
        ]
        # 2D dummy embeddings
        embeddings = [
            [1.0, 0.0],  # AI
            [0.0, 1.0],  # Cooking
            [0.9, 0.1],  # ML
        ]
        store.add_documents(docs, embeddings)

        # Query vector aligned with AI [1.0, 0.0]
        results = store.similarity_search([1.0, 0.0], top_k=2)
        assert len(results) == 2
        assert results[0].id == "doc_ai"
        assert results[1].id == "doc_ml"

    def test_reciprocal_rank_fusion(self):
        dense = ["doc1", "doc2", "doc3"]
        sparse = ["doc2", "doc4", "doc1"]

        # doc2 is rank 1 in sparse, rank 2 in dense -> Highest combined RRF score
        fused = reciprocal_rank_fusion(dense, sparse, k=60)

        assert fused[0] == "doc2"
        assert "doc1" in fused
        assert "doc3" in fused
        assert "doc4" in fused
