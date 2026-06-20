import pytest
from unittest.mock import patch, MagicMock
from src.agent.graph import build_graph

@pytest.fixture(scope="module")
def graph():
    return build_graph()

class TestFullPipeline:

    @patch("src.rag.retriever.chromadb.PersistentClient")
    @patch("src.utils.gemini_client.RateLimitedGeminiClient.generate")
    def test_technical_query_end_to_end(self, mock_generate, mock_chroma, graph):
        # Mock ChromaDB query to return valid docs
        mock_coll = MagicMock()
        mock_coll.query.return_value = {
            "documents": [["API OAuth Authentication Guide: Set Authorization header to Bearer."]],
            "metadatas": [[{"source": "api_authentication_errors.txt", "chunk_id": "c1"}]],
            "distances": [[0.15]]
        }
        mock_chroma.return_value.get_collection.return_value = mock_coll

        # Mock LLM calls:
        # First call is for persona detection (in persona_node)
        # Second call is for response generation (in response_node)
        mock_generate.side_effect = [
            '{"persona": "TECHNICAL_EXPERT", "confidence": 0.95, "reasoning": "Uses API/OAuth terms"}', # Persona classification
            "To fix OAuth 401 error, make sure your token is active. [Source: api_authentication_errors.txt]" # Response generation
        ]

        state = graph.invoke({
            "current_message": "How do I fix OAuth 401 errors when calling the API?",
            "messages": [], "turn_count": 0, "sentiment_scores": [],
            "attempted_steps": [], "resolution_attempts": 0, "escalate": False
        })
        assert state["persona"] == "TECHNICAL_EXPERT"
        assert len(state["retrieved_chunks"]) >= 1
        assert state["response"] != ""
        assert not state["escalate"]

    @patch("src.rag.retriever.chromadb.PersistentClient")
    @patch("src.utils.gemini_client.RateLimitedGeminiClient.generate")
    def test_frustrated_user_escalates_after_multiple_failures(self, mock_generate, mock_chroma, graph):
        # Mock ChromaDB query
        mock_coll = MagicMock()
        mock_coll.query.return_value = {
            "documents": [["Password Reset Steps"]],
            "metadatas": [[{"source": "password_reset_guide.txt", "chunk_id": "c2"}]],
            "distances": [[0.12]]
        }
        mock_chroma.return_value.get_collection.return_value = mock_coll

        # Mock LLM calls:
        # First is persona detection
        # Second is HandoffBuilder issue summary
        # Third is HandoffBuilder next steps
        mock_generate.side_effect = [
            '{"persona": "FRUSTRATED_USER", "confidence": 0.96, "reasoning": "Urgent customer lockout"}', # Persona detection
            "Customer has been locked out of account for 2 hours.", # Handoff issue summary
            "- Verify user logs\n- Check IP whitelist\n- Reset token manually" # Handoff next steps
        ]

        initial_state = {
            "current_message": "I need to speak to a manager now, this is unacceptable!!!",
            "messages": [
                {"role": "user", "content": "Nothing works"},
                {"role": "assistant", "content": "Try these steps..."},
                {"role": "user", "content": "Still broken!!!"},
            ],
            "turn_count": 3,
            "sentiment_scores": [-0.4, -0.6],
            "attempted_steps": ["Reset password", "Clear cache"],
            "resolution_attempts": 2,
            "escalate": False
        }
        state = graph.invoke(initial_state)
        assert state["escalate"] is True
        assert state["handoff_summary"] is not None
        assert state["handoff_summary"]["persona"] == "FRUSTRATED_USER"

    @patch("src.rag.retriever.chromadb.PersistentClient")
    @patch("src.utils.gemini_client.RateLimitedGeminiClient.generate")
    def test_business_executive_gets_concise_response(self, mock_generate, mock_chroma, graph):
        # Mock ChromaDB query
        mock_coll = MagicMock()
        mock_coll.query.return_value = {
            "documents": [["SLA Credit Guarantee Policy: NovaSuite has 99.9% uptime commitments."]],
            "metadatas": [[{"source": "novasuite_sla_policy.pdf", "chunk_id": "c3"}]],
            "distances": [[0.1]]
        }
        mock_chroma.return_value.get_collection.return_value = mock_coll

        # Mock LLM calls:
        # First is persona detection
        # Second is response generation
        mock_generate.side_effect = [
            '{"persona": "BUSINESS_EXECUTIVE", "confidence": 0.92, "reasoning": "Asks about SLA credit timelines"}', # Persona detection
            "NovaSuite committed uptime is 99.9%. Credit eligibility is 10-50% back. [Source: novasuite_sla_policy.pdf]" # Response generation
        ]

        state = graph.invoke({
            "current_message": "What is the SLA impact of this outage on our contract?",
            "messages": [], "turn_count": 0, "sentiment_scores": [],
            "attempted_steps": [], "resolution_attempts": 0, "escalate": False
        })
        assert state["persona"] == "BUSINESS_EXECUTIVE"
        assert len(state["response"]) <= 1200  # Concise response expected
        assert not state["escalate"]
