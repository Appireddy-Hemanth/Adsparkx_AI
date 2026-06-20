import pytest
from unittest.mock import patch
from src.escalation.handoff import HandoffBuilder

class TestHandoffSummary:

    @patch.object(HandoffBuilder, "_call_llm", return_value="Issue summary and next steps mock")
    def test_summary_has_all_required_fields(self, mock_llm):
        builder = HandoffBuilder()
        summary = builder.build(
            persona="FRUSTRATED_USER",
            persona_confidence=0.91,
            messages=[{"role": "user", "content": "I can't login!"}],
            retrieved_chunks=[{"source": "password_reset_guide.txt", "text": "...", "score": 0.88}],
            attempted_steps=["Password reset"],
            sentiment_scores=[-0.62],
            escalation_reason="negative_sentiment_trend",
        )
        required_keys = ["persona", "persona_confidence", "issue_summary",
                         "conversation_history", "documents_used",
                         "attempted_steps", "escalation_reason",
                         "recommended_next_steps", "session_id",
                         "escalated_at", "priority"]
        for key in required_keys:
            assert key in summary, f"Missing key: {key}"

    @patch.object(HandoffBuilder, "_call_llm", return_value="Issue summary mock")
    def test_priority_is_p1_for_very_negative_sentiment(self, mock_llm):
        builder = HandoffBuilder()
        summary = builder.build(
            persona="FRUSTRATED_USER",
            persona_confidence=0.95,
            messages=[],
            retrieved_chunks=[],
            attempted_steps=[],
            sentiment_scores=[-0.85, -0.90],
            escalation_reason="negative_sentiment",
        )
        assert summary["priority"] == "P1"

    @patch.object(HandoffBuilder, "_call_llm", return_value="Issue summary mock")
    def test_documents_used_extracted_from_chunks(self, mock_llm):
        builder = HandoffBuilder()
        summary = builder.build(
            persona="TECHNICAL_EXPERT",
            persona_confidence=0.80,
            messages=[],
            retrieved_chunks=[
                {"source": "api_authentication_errors.txt", "text": "...", "score": 0.9},
                {"source": "rate_limiting_policy.md", "text": "...", "score": 0.75},
            ],
            attempted_steps=[],
            sentiment_scores=[0.0],
            escalation_reason="low_confidence",
        )
        assert "api_authentication_errors.txt" in summary["documents_used"]
        assert "rate_limiting_policy.md" in summary["documents_used"]
