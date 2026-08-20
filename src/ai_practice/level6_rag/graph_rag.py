from typing import Any, Literal

from pydantic import BaseModel, Field


class Entity(BaseModel):
    """Knowledge Graph Entity (Node)."""

    id: str
    name: str
    entity_type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class Relation(BaseModel):
    """Knowledge Graph Directed Relation (Edge)."""

    source_id: str
    target_id: str
    relation_type: str
    properties: dict[str, Any] = Field(default_factory=dict)


class KnowledgeGraph:
    """In-memory Knowledge Graph supporting entity/relation indexing and k-hop subgraph traversal."""

    def __init__(self) -> None:
        self.entities: dict[str, Entity] = {}
        self.relations: list[Relation] = []

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the graph."""
        # TODO: entity_id를 키로 하여 self.entities에 엔티티를 등록하세요.
        raise NotImplementedError

    def add_relation(self, relation: Relation) -> None:
        """Add a directed relation between existing entities.

        Raises:
            ValueError: If either source_id or target_id does not exist in self.entities.
        """
        # TODO: source와 target 엔티티가 모두 존재하는지 확인하고(없으면 ValueError 발생),
        #       관계 목록 및 인접 리스트 등에 추가하세요.
        raise NotImplementedError

    def get_entity(self, entity_id: str) -> Entity | None:
        """Get an entity by its ID."""
        # TODO: ID에 해당하는 Entity를 조회하여 반환하세요 (없으면 None).
        raise NotImplementedError

    def get_neighbors(
        self, entity_id: str, direction: Literal["out", "in", "both"] = "both"
    ) -> list[tuple[Relation, Entity]]:
        """Return connected (relation, neighbor_entity) pairs based on traversal direction.

        Args:
            entity_id: The center entity id.
            direction: 'out' (outgoing edges), 'in' (incoming edges), or 'both'.
        """
        # TODO: 지정된 방향('out', 'in', 'both')에 따라 연결된 (Relation, Entity) 튜플 목록을 반환하세요.
        raise NotImplementedError

    def find_subgraph(
        self, seed_entity_ids: list[str], max_hops: int = 1
    ) -> tuple[set[str], list[Relation]]:
        """Traverse the graph from seed entities using BFS up to max_hops.

        Returns:
            A tuple of (visited_entity_ids, subgraph_relations).
        """
        # TODO: BFS 알고리즘을 사용하여 seed_entity_ids부터 최대 max_hops 거리 이내의
        #       방문된 엔티티 ID 집합(set[str])과 탐색된 관계 목록(list[Relation])을 반환하세요.
        #       (순환 참조/사이클이 발생해도 무한 루프에 빠지지 않도록 처리해야 합니다.)
        raise NotImplementedError


class GraphRAGRetriever:
    """Graph-based context retriever for LLM prompt augmentation."""

    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph

    def extract_seed_entities(self, query: str) -> list[str]:
        """Extract entity IDs mentioned in query by entity name (case-insensitive substring match)."""
        # TODO: 그래프에 등록된 엔티티들의 이름(name)이 query 텍스트(대소문자 무시)에
        #       포함되어 있는 엔티티들의 ID 목록을 추출하여 반환하세요.
        raise NotImplementedError

    def format_triples(self, relations: list[Relation]) -> list[str]:
        """Format relations into human-readable triple strings.

        Format:
            "(SourceName: SourceType) -[RELATION_TYPE]-> (TargetName: TargetType)"
        """
        # TODO: Relation 목록을 '(Source: Type) -[REL_TYPE]-> (Target: Type)' 형식의 문자열 리스트로 변환하세요.
        raise NotImplementedError

    def retrieve_context(self, query: str, max_hops: int = 1) -> str:
        """Retrieve structured graph context for a query string.

        Output format example:
            [Knowledge Graph Context]
            Entities:
            - OpenAI (Organization)
            - GPT-4 (LanguageModel)

            Relationships:
            - (OpenAI: Organization) -[DEVELOPED]-> (GPT-4: LanguageModel)

        Returns empty string ("") if no seed entities or relevant subgraph is found.
        """
        # TODO: 쿼리에서 시드 엔티티를 추출하고, k-hop 서브그래프를 탐색한 후,
        #       LLM 프롬프트에 주입 가능한 포맷팅된 컨텍스트 문자열을 생성하여 반환하세요.
        #       (매칭된 엔티티가 없으면 빈 문자열 ""을 반환합니다.)
        raise NotImplementedError
