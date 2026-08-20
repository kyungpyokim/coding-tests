from collections import defaultdict, deque
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
        self._adj_out: dict[str, list[Relation]] = defaultdict(list)
        self._adj_in: dict[str, list[Relation]] = defaultdict(list)

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the graph."""
        self.entities[entity.id] = entity

    def add_relation(self, relation: Relation) -> None:
        """Add a directed relation between existing entities."""
        if (
            relation.source_id not in self.entities
            or relation.target_id not in self.entities
        ):
            raise ValueError("Both source and target entities must exist in the graph.")

        self.relations.append(relation)
        self._adj_out[relation.source_id].append(relation)
        self._adj_in[relation.target_id].append(relation)

    def get_entity(self, entity_id: str) -> Entity | None:
        """Get an entity by its ID."""
        return self.entities.get(entity_id)

    def get_neighbors(
        self, entity_id: str, direction: Literal["out", "in", "both"] = "both"
    ) -> list[tuple[Relation, Entity]]:
        """Return connected (relation, neighbor_entity) pairs based on traversal direction."""
        neighbors: list[tuple[Relation, Entity]] = []

        if direction in ("out", "both"):
            for rel in self._adj_out.get(entity_id, []):
                target = self.entities.get(rel.target_id)
                if target:
                    neighbors.append((rel, target))

        if direction in ("in", "both"):
            for rel in self._adj_in.get(entity_id, []):
                source = self.entities.get(rel.source_id)
                if source:
                    neighbors.append((rel, source))

        return neighbors

    def find_subgraph(
        self, seed_entity_ids: list[str], max_hops: int = 1
    ) -> tuple[set[str], list[Relation]]:
        """Traverse the graph from seed entities using BFS up to max_hops.

        Returns:
            A tuple of (visited_entity_ids, subgraph_relations).
        """
        valid_seeds = [eid for eid in seed_entity_ids if eid in self.entities]
        if not valid_seeds:
            return set(), []

        visited_nodes: set[str] = set(valid_seeds)
        discovered_relations: list[Relation] = []
        seen_relation_keys: set[tuple[str, str, str]] = set()

        queue: deque[tuple[str, int]] = deque((eid, 0) for eid in valid_seeds)

        while queue:
            curr_node, current_hop = queue.popleft()
            if current_hop >= max_hops:
                continue

            for rel, neighbor in self.get_neighbors(curr_node, direction="both"):
                rel_key = (rel.source_id, rel.target_id, rel.relation_type)
                if rel_key not in seen_relation_keys:
                    seen_relation_keys.add(rel_key)
                    discovered_relations.append(rel)

                if neighbor.id not in visited_nodes:
                    visited_nodes.add(neighbor.id)
                    queue.append((neighbor.id, current_hop + 1))

        return visited_nodes, discovered_relations


class GraphRAGRetriever:
    """Graph-based context retriever for LLM prompt augmentation."""

    def __init__(self, graph: KnowledgeGraph) -> None:
        self.graph = graph

    def extract_seed_entities(self, query: str) -> list[str]:
        """Extract entity IDs mentioned in query by entity name (case-insensitive substring match)."""
        query_lower = query.lower()
        matched_ids: list[str] = []

        for entity_id, entity in self.graph.entities.items():
            if entity.name.lower() in query_lower:
                matched_ids.append(entity_id)

        return matched_ids

    def format_triples(self, relations: list[Relation]) -> list[str]:
        """Format relations into human-readable triple strings."""
        formatted: list[str] = []
        for rel in relations:
            source = self.graph.get_entity(rel.source_id)
            target = self.graph.get_entity(rel.target_id)
            if source and target:
                formatted.append(
                    f"({source.name}: {source.entity_type}) -[{rel.relation_type}]-> ({target.name}: {target.entity_type})"
                )
        return formatted

    def retrieve_context(self, query: str, max_hops: int = 1) -> str:
        """Retrieve structured graph context for a query string."""
        seed_ids = self.extract_seed_entities(query)
        if not seed_ids:
            return ""

        node_ids, relations = self.graph.find_subgraph(seed_ids, max_hops=max_hops)
        if not node_ids:
            return ""

        entities = [self.graph.entities[nid] for nid in sorted(node_ids)]
        triples = self.format_triples(relations)

        lines: list[str] = ["[Knowledge Graph Context]"]
        lines.append("Entities:")
        for entity in entities:
            lines.append(f"- {entity.name} ({entity.entity_type})")

        if triples:
            lines.append("\nRelationships:")
            for triple in triples:
                lines.append(f"- {triple}")

        return "\n".join(lines)
