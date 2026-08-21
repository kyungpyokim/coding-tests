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
    # TODO: 긴 텍스트를 chunk_size 크기로 자르고, 이전 청크와 overlap만큼 겹치도록 분할하여 반환하세요.
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


class InMemoryVectorStore:
    """In-memory dense vector store with cosine similarity retrieval."""

    def __init__(self) -> None:
        self.docs: list[Document] = []
        self.embeddings: list[list[float]] = []

    def add_documents(
        self, docs: list[Document], embeddings: list[list[float]]
    ) -> None:
        """Store documents and their corresponding vector embeddings."""
        # TODO: 문서와 임베딩 벡터 목록을 저장소에 보관하세요.
        raise NotImplementedError

    def similarity_search(
        self, query_embedding: list[float], top_k: int = 3
    ) -> list[Document]:
        """Search top-k most similar documents based on cosine similarity."""
        # TODO: query_embedding과 저장된 임베딩들 간의 코사인 유사도를 계산하여 상위 top_k개 문서를 반환하세요.
        raise NotImplementedError


def reciprocal_rank_fusion(
    dense_results: list[str], sparse_results: list[str], k: int = 60
) -> list[str]:
    """Combine dense and sparse search rankings using Reciprocal Rank Fusion (RRF).

    Formula for each doc d: Score(d) = sum(1 / (k + rank(d)))
    Returns doc ids sorted by descending RRF score.
    """
    # TODO: Dense 결과 순위와 Sparse 결과 순위를 RRF 점수로 합산하여 최종 정렬된 문서 ID 목록을 반환하세요.
    raise NotImplementedError
