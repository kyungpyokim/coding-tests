import pytest

from ai_practice.level6_rag.graph_rag import (
    Entity,
    GraphRAGRetriever,
    KnowledgeGraph,
    Relation,
)


@pytest.mark.unit
class TestGraphRAG:
    @pytest.fixture
    def sample_graph(self) -> KnowledgeGraph:
        graph = KnowledgeGraph()
        # Entities
        graph.add_entity(
            Entity(id="e_openai", name="OpenAI", entity_type="Organization")
        )
        graph.add_entity(Entity(id="e_gpt4", name="GPT-4", entity_type="LanguageModel"))
        graph.add_entity(Entity(id="e_sam", name="Sam Altman", entity_type="Person"))
        graph.add_entity(Entity(id="e_python", name="Python", entity_type="Language"))

        # Relations
        graph.add_relation(
            Relation(
                source_id="e_openai",
                target_id="e_gpt4",
                relation_type="DEVELOPED",
            )
        )
        graph.add_relation(
            Relation(
                source_id="e_sam",
                target_id="e_openai",
                relation_type="CEO_OF",
            )
        )
        graph.add_relation(
            Relation(
                source_id="e_gpt4",
                target_id="e_python",
                relation_type="SUPPORTS",
            )
        )
        return graph

    def test_add_and_get_entity(self):
        graph = KnowledgeGraph()
        entity = Entity(
            id="e1",
            name="LangChain",
            entity_type="Framework",
            properties={"version": "1.0"},
        )
        graph.add_entity(entity)

        retrieved = graph.get_entity("e1")
        assert retrieved is not None
        assert retrieved.name == "LangChain"
        assert retrieved.properties["version"] == "1.0"
        assert graph.get_entity("non_existent") is None

    def test_add_relation_requires_existing_entities(self):
        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="e1", name="A", entity_type="TypeA"))

        # Target entity 'e2' doesn't exist
        with pytest.raises(
            ValueError, match="Both source and target entities must exist"
        ):
            graph.add_relation(
                Relation(source_id="e1", target_id="e2", relation_type="REL")
            )

    def test_get_neighbors_direction(self, sample_graph: KnowledgeGraph):
        # OpenAI has OUT: GPT-4 (DEVELOPED), IN: Sam Altman (CEO_OF)
        out_neighbors = sample_graph.get_neighbors("e_openai", direction="out")
        assert len(out_neighbors) == 1
        rel, neighbor = out_neighbors[0]
        assert rel.relation_type == "DEVELOPED"
        assert neighbor.id == "e_gpt4"

        in_neighbors = sample_graph.get_neighbors("e_openai", direction="in")
        assert len(in_neighbors) == 1
        rel, neighbor = in_neighbors[0]
        assert rel.relation_type == "CEO_OF"
        assert neighbor.id == "e_sam"

        both_neighbors = sample_graph.get_neighbors("e_openai", direction="both")
        assert len(both_neighbors) == 2
        neighbor_ids = {n.id for _, n in both_neighbors}
        assert neighbor_ids == {"e_gpt4", "e_sam"}

    def test_find_subgraph_k_hop(self, sample_graph: KnowledgeGraph):
        # 1-hop from OpenAI -> OpenAI, GPT-4, Sam Altman
        node_ids, relations = sample_graph.find_subgraph(
            seed_entity_ids=["e_openai"], max_hops=1
        )
        assert node_ids == {"e_openai", "e_gpt4", "e_sam"}
        assert len(relations) == 2
        rel_types = {r.relation_type for r in relations}
        assert rel_types == {"DEVELOPED", "CEO_OF"}

        # 2-hop from Sam Altman -> Sam Altman -> OpenAI -> GPT-4 -> Python
        node_ids_2hop, relations_2hop = sample_graph.find_subgraph(
            seed_entity_ids=["e_sam"], max_hops=3
        )
        assert node_ids_2hop == {"e_sam", "e_openai", "e_gpt4", "e_python"}
        assert len(relations_2hop) == 3

    def test_find_subgraph_with_cycle(self):
        graph = KnowledgeGraph()
        graph.add_entity(Entity(id="a", name="A", entity_type="Node"))
        graph.add_entity(Entity(id="b", name="B", entity_type="Node"))
        graph.add_relation(Relation(source_id="a", target_id="b", relation_type="TO"))
        graph.add_relation(Relation(source_id="b", target_id="a", relation_type="BACK"))

        # Should not infinite loop and should return both nodes and relations
        nodes, relations = graph.find_subgraph(seed_entity_ids=["a"], max_hops=5)
        assert nodes == {"a", "b"}
        assert len(relations) == 2

    def test_extract_seed_entities(self, sample_graph: KnowledgeGraph):
        retriever = GraphRAGRetriever(sample_graph)

        # Exact and case-insensitive query match
        query = "Who is the CEO of openai and what did they build with gpt-4?"
        seeds = retriever.extract_seed_entities(query)
        assert "e_openai" in seeds
        assert "e_gpt4" in seeds
        assert "e_sam" not in seeds

    def test_format_triples(self, sample_graph: KnowledgeGraph):
        retriever = GraphRAGRetriever(sample_graph)
        relations = [
            Relation(
                source_id="e_openai",
                target_id="e_gpt4",
                relation_type="DEVELOPED",
            )
        ]
        triples = retriever.format_triples(relations)
        assert len(triples) == 1
        assert (
            triples[0] == "(OpenAI: Organization) -[DEVELOPED]-> (GPT-4: LanguageModel)"
        )

    def test_retrieve_context_end_to_end(self, sample_graph: KnowledgeGraph):
        retriever = GraphRAGRetriever(sample_graph)
        query = "Tell me about GPT-4 and its creator OpenAI."

        context = retriever.retrieve_context(query, max_hops=1)
        assert "[Knowledge Graph Context]" in context
        assert "Entities:" in context
        assert "OpenAI (Organization)" in context
        assert "GPT-4 (LanguageModel)" in context
        assert "Relationships:" in context
        assert "(OpenAI: Organization) -[DEVELOPED]-> (GPT-4: LanguageModel)" in context

    def test_retrieve_context_no_match(self, sample_graph: KnowledgeGraph):
        retriever = GraphRAGRetriever(sample_graph)
        query = "Something completely unrelated like bananas and apples."

        context = retriever.retrieve_context(query, max_hops=1)
        assert context == ""
