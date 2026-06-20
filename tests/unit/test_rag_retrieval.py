import pytest
from unittest.mock import MagicMock, patch
from src.rag.retriever import KBRetriever

@pytest.fixture
def mock_collection():
    coll = MagicMock()
    # Mock return values for collection.query
    coll.query.return_value = {
        "documents": [["Reset steps... Content here", "Another document", "API documentation"]],
        "metadatas": [[{"source": "password_reset_guide.txt", "chunk_id": "c1"}, {"source": "billing_faq.txt", "chunk_id": "c2"}, {"source": "api.md", "chunk_id": "c3"}]],
        "distances": [[0.1, 0.4, 0.95]]
    }
    return coll

class TestRAGRetrieval:

    @patch("src.rag.retriever.chromadb.PersistentClient")
    def test_retriever_returns_results_for_known_query(self, mock_client, mock_collection):
        # Setup mock client
        mock_client.return_value.get_collection.return_value = mock_collection
        
        retriever = KBRetriever()
        chunks = retriever.retrieve("how to reset password", top_k=3)
        assert len(chunks) >= 1

    @patch("src.rag.retriever.chromadb.PersistentClient")
    def test_retriever_returns_confidence_score(self, mock_client, mock_collection):
        mock_client.return_value.get_collection.return_value = mock_collection
        
        retriever = KBRetriever()
        chunks = retriever.retrieve("OAuth token expiry", top_k=3)
        assert all(hasattr(c, "score") for c in chunks)
        assert all(0.0 <= c.score <= 1.0 for c in chunks)

    @patch("src.rag.retriever.chromadb.PersistentClient")
    def test_chunk_has_required_metadata(self, mock_client, mock_collection):
        mock_client.return_value.get_collection.return_value = mock_collection
        
        retriever = KBRetriever()
        chunks = retriever.retrieve("billing refund policy", top_k=1)
        assert len(chunks) >= 1
        c = chunks[0]
        assert c.metadata.get("source") is not None
        assert c.metadata.get("chunk_id") is not None

    @patch("src.rag.retriever.chromadb.PersistentClient")
    def test_irrelevant_query_returns_low_confidence(self, mock_client):
        # Mock poor distance match (e.g. distance = 1.8)
        poor_collection = MagicMock()
        poor_collection.query.return_value = {
            "documents": [["How to make pizza..."]],
            "metadatas": [[{"source": "pizza.txt", "chunk_id": "c_pizza"}]],
            "distances": [[1.8]]
        }
        mock_client.return_value.get_collection.return_value = poor_collection
        
        retriever = KBRetriever()
        chunks = retriever.retrieve("best pizza recipe in Rome", top_k=3)
        if chunks:
            assert chunks[0].score < 0.60  # Low relevance expected since distance is 1.8 (score = 1 - 1.8 = -0.8 clamped or raw)

    @patch("src.rag.retriever.chromadb.PersistentClient")
    def test_top_k_respected(self, mock_client, mock_collection):
        mock_client.return_value.get_collection.return_value = mock_collection
        
        retriever = KBRetriever()
        chunks = retriever.retrieve("API authentication", top_k=2)
        assert len(chunks) <= 2
