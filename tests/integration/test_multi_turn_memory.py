import pytest
from unittest.mock import patch, MagicMock
from src.agent.graph import build_graph

class TestMultiTurnMemory:

    @patch("src.rag.retriever.chromadb.PersistentClient")
    @patch("src.utils.gemini_client.RateLimitedGeminiClient.generate")
    def test_conversation_history_grows_across_turns(self, mock_generate, mock_chroma):
        graph = build_graph()
        
        # Mock ChromaDB query
        mock_coll = MagicMock()
        mock_coll.query.return_value = {
            "documents": [["MFA Configuration Guide: Scan QR code using Google Authenticator."]],
            "metadatas": [[{"source": "mfa_setup_guide.md", "chunk_id": "c_mfa"}]],
            "distances": [[0.15]]
        }
        mock_chroma.return_value.get_collection.return_value = mock_coll

        # Mock LLM calls:
        # Turn 1: 1. Persona classification, 2. Response generation
        # Turn 2: 1. Persona classification, 2. Response generation
        mock_generate.side_effect = [
            '{"persona": "FRUSTRATED_USER", "confidence": 0.85, "reasoning": "First query"}',
            "Scan the QR code to set up MFA. [Source: mfa_setup_guide.md]",
            '{"persona": "FRUSTRATED_USER", "confidence": 0.88, "reasoning": "Follow up"}',
            "Verify your authenticator app is synced. [Source: mfa_setup_guide.md]"
        ]

        state = graph.invoke({
            "current_message": "How do I set up MFA?",
            "messages": [], "turn_count": 0, "sentiment_scores": [],
            "attempted_steps": [], "resolution_attempts": 0, "escalate": False
        })
        assert state["turn_count"] == 1
        assert len(state["messages"]) == 2  # user + assistant

        state2 = graph.invoke({
            **state,
            "current_message": "And how do I disable it temporarily?",
        })
        assert state2["turn_count"] == 2
        assert len(state2["messages"]) == 4

    @patch("src.rag.retriever.chromadb.PersistentClient")
    @patch("src.utils.gemini_client.RateLimitedGeminiClient.generate")
    def test_attempted_steps_accumulated_across_turns(self, mock_generate, mock_chroma):
        graph = build_graph()
        
        # Mock ChromaDB query
        mock_coll = MagicMock()
        mock_coll.query.return_value = {
            "documents": [["Account Lockout details."]],
            "metadatas": [[{"source": "account_lock_troubleshooting.txt", "chunk_id": "c_lock"}]],
            "distances": [[0.1]]
        }
        mock_chroma.return_value.get_collection.return_value = mock_coll

        # Mock LLM calls:
        # Turn 1: 1. Persona detection, 2. Response generation with a step
        # Turn 2: 1. Persona detection, 2. Response generation with another step
        mock_generate.side_effect = [
            '{"persona": "FRUSTRATED_USER", "confidence": 0.80, "reasoning": "Reset password request"}',
            "1. Try password reset via email link. [Source: account_lock_troubleshooting.txt]",
            '{"persona": "FRUSTRATED_USER", "confidence": 0.85, "reasoning": "Lockout feedback"}',
            "2. Contact administrator to manually unlock account. [Source: account_lock_troubleshooting.txt]"
        ]

        state = graph.invoke({
            "current_message": "My account is locked",
            "messages": [], "turn_count": 0, "sentiment_scores": [],
            "attempted_steps": [], "resolution_attempts": 0, "escalate": False
        })
        initial_steps = len(state["attempted_steps"])
        assert initial_steps >= 1

        state2 = graph.invoke({
            **state,
            "current_message": "I tried that and it still doesn't work",
        })
        # After second turn, steps list should be same or grow
        assert len(state2["attempted_steps"]) >= initial_steps
        assert "Contact administrator to manually unlock account." in state2["attempted_steps"]
