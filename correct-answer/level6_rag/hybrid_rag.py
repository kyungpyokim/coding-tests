import math
from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    """Document data structure with ID, content and metadata."""

    id: str
    content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


def recursive_character_chunk(
    text: str, chunk_size: int = 100, overlap: int = 20
) -> list[str]:
    """Split text into chunks of maximum `chunk_size` characters with `overlap`."""
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    step = chunk_size - overlap

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start += step

    return chunks


def _cosine_similarity(v1: list[float], v2: list[float]) -> float:
    dot = sum(a * b for a, b in zip(v1, v2, strict=False))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


class InMemoryVectorStore:
    """In-memory dense vector store with cosine similarity retrieval."""

    def __init__(self) -> None:
        self.docs: list[Document] = []
        self.embeddings: list[list[float]] = []

    def add_documents(
        self, docs: list[Document], embeddings: list[list[float]]
    ) -> None:
        """Store documents and their corresponding vector embeddings."""
        self.docs.extend(docs)
        self.embeddings.extend(embeddings)

    def similarity_search(
        self, query_embedding: list[float], top_k: int = 3
    ) -> list[Document]:
        """Search top-k most similar documents based on cosine similarity."""
        if not self.docs:
            return []

        scores: list[tuple[float, Document]] = []
        for doc, emb in zip(self.docs, self.embeddings, strict=False):
            sim = _cosine_similarity(query_embedding, emb)
            scores.append((sim, doc))

        # Sort by similarity descending
        scores.sort(key=lambda x: x[0], reverse=True)
        return [doc for _, doc in scores[:top_k]]


def reciprocal_rank_fusion(
    dense_results: list[str], sparse_results: list[str], k: int = 60
) -> list[str]:
    """Combine dense and sparse search rankings using Reciprocal Rank Fusion (RRF)."""
    scores: dict[str, float] = {}

    for rank, doc_id in enumerate(dense_results, start=1):
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank))

    for rank, doc_id in enumerate(sparse_results, start=1):
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank))

    sorted_docs = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return [doc_id for doc_id, _ in sorted_docs]
