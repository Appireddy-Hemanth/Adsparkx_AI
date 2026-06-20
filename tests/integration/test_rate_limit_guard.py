import pytest
import time
from unittest.mock import patch, MagicMock
from src.utils.gemini_client import RateLimitedGeminiClient
from src.agent.graph import build_graph

class TestRateLimitGuardIntegration:

    @patch("src.rag.retriever.chromadb.PersistentClient")
    @patch("src.utils.gemini_client.RateLimitedGeminiClient.generate")
    def test_rate_limit_guard_warning_threshold(self, mock_generate, mock_chroma):
        """Verify that when total daily call count exceeds 1200 (80%), rate_limit_warning is True."""
        graph = build_graph()
        
        # Mock ChromaDB query
        mock_coll = MagicMock()
        mock_coll.query.return_value = {
            "documents": [["MFA Configuration Guide: Scan QR code using Google Authenticator."]],
            "metadatas": [[{"source": "mfa_setup_guide.md", "chunk_id": "c_mfa"}]],
            "distances": [[0.15]]
        }
        mock_chroma.return_value.get_collection.return_value = mock_coll

        # Mock LLM calls
        mock_generate.side_effect = [
            '{"persona": "TECHNICAL_EXPERT", "confidence": 0.85, "reasoning": "MFA query"}',
            "Scan the QR code to set up MFA. [Source: mfa_setup_guide.md]"
        ]

        # Artificially set daily call counter to 1250 across client types (exceeding 80% threshold of 1500)
        RateLimitedGeminiClient._shared_daily_counts.clear()
        RateLimitedGeminiClient._shared_daily_counts["gemini-2.5-flash-lite"] = 650
        RateLimitedGeminiClient._shared_daily_counts["gemini-2.5-flash"] = 600

        state = graph.invoke({
            "current_message": "How do I set up MFA?",
            "messages": [], "turn_count": 0, "sentiment_scores": [],
            "attempted_steps": [], "resolution_attempts": 0, "escalate": False
        })
        assert state["gemini_daily_calls"] >= 1250
        assert state["rate_limit_warning"] is True

    def test_rate_limit_guard_throttles_rapid_requests(self):
        """Verify that rate guard sleeps when RPM limit is reached in the integration path."""
        client = RateLimitedGeminiClient("gemini-2.5-flash-lite", api_key="test")
        
        # Inject 15 request timestamps in the last 10 seconds to trigger enforcement
        now = time.time()
        client._request_timestamps.clear()
        for i in range(15):
            client._request_timestamps.append(now - 10)
            
        with patch.object(client.model, "generate_content", return_value=MagicMock(text="Success")):
            with patch("time.sleep") as mock_sleep:
                client.generate("test prompt")
                assert mock_sleep.called
                # Sleep time should be roughly 60 - (now - oldest_timestamp (now-10)) = 50s
                sleep_arg = mock_sleep.call_args[0][0]
                assert 45.0 <= sleep_arg <= 51.0
