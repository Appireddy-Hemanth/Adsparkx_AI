import pytest
from unittest.mock import MagicMock, patch
from src.agent.nodes.response_node import ResponseNode

class TestResponseGeneration:

    def test_response_contains_source_citation(self):
        node = ResponseNode()
        mock_chunks = [{"source": "password_reset_guide.txt", "text": "Reset steps...", "score": 0.88}]
        with patch.object(node, "_call_llm", return_value="Here are the steps... [Source: password_reset_guide.txt]"):
            state = {
                "persona": "FRUSTRATED_USER",
                "retrieved_chunks": mock_chunks,
                "retrieval_confidence": 0.88,
                "current_message": "I can't login",
                "messages": [],
                "attempted_steps": []
            }
            result = node.run(state)
            assert "Source:" in result["response"]

    def test_no_response_generated_when_no_chunks(self):
        node = ResponseNode()
        state = {
            "persona": "FRUSTRATED_USER",
            "retrieved_chunks": [],
            "retrieval_confidence": 0.20,
            "current_message": "random query",
            "messages": []
        }
        result = node.run(state)
        assert result.get("escalate") is True

    def test_technical_prompt_used_for_technical_persona(self):
        node = ResponseNode()
        with patch.object(node, "_call_llm") as mock_llm:
            mock_llm.return_value = "Technical response [Source: api_ref.md]"
            state = {
                "persona": "TECHNICAL_EXPERT",
                "retrieved_chunks": [{"source": "api_ref.md", "text": "...", "score": 0.85}],
                "retrieval_confidence": 0.85,
                "current_message": "API error 401",
                "messages": [],
                "attempted_steps": []
            }
            node.run(state)
            call_args = mock_llm.call_args
            # Verify the prompt contained technical-specific instructions
            assert "technical" in str(call_args).lower() or "root cause" in str(call_args).lower()

    def test_response_generation_escalates_on_exception(self):
        node = ResponseNode()
        with patch.object(node, "_call_llm", side_effect=Exception("API failure")):
            state = {
                "persona": "TECHNICAL_EXPERT",
                "retrieved_chunks": [{"source": "api_ref.md", "text": "...", "score": 0.85}],
                "retrieval_confidence": 0.85,
                "current_message": "API error 401",
                "messages": [],
                "attempted_steps": []
            }
            result = node.run(state)
            assert result.get("escalate") is True
            assert result.get("escalation_reason") == "response_generation_failure"
