import pytest
from unittest.mock import patch, MagicMock
from src.personas.detector import PersonaDetector

@pytest.fixture
def detector():
    return PersonaDetector()

class TestPersonaDetection:

    def test_technical_expert_detected_from_api_question(self, detector):
        msg = "Can you explain the API authentication failure and provide error details?"
        with patch.object(detector, "_call_llm", return_value='{"persona": "TECHNICAL_EXPERT", "confidence": 0.95, "reasoning": "Uses API technical term"}'):
            result = detector.classify(msg, history=[])
            assert result.persona == "TECHNICAL_EXPERT"
            assert result.confidence >= 0.70

    def test_frustrated_user_detected_from_emotional_message(self, detector):
        msg = "I've tried everything and nothing works! This is terrible!!!"
        with patch.object(detector, "_call_llm", return_value='{"persona": "FRUSTRATED_USER", "confidence": 0.90, "reasoning": "Urgent and emotional"}'):
            result = detector.classify(msg, history=[])
            assert result.persona == "FRUSTRATED_USER"
            assert result.confidence >= 0.70

    def test_business_executive_detected_from_impact_question(self, detector):
        msg = "How does this issue impact operations and when will it be resolved?"
        with patch.object(detector, "_call_llm", return_value='{"persona": "BUSINESS_EXECUTIVE", "confidence": 0.88, "reasoning": "Impact and timeline question"}'):
            result = detector.classify(msg, history=[])
            assert result.persona == "BUSINESS_EXECUTIVE"
            assert result.confidence >= 0.70

    def test_persona_result_has_required_fields(self, detector):
        msg = "my account is locked"
        with patch.object(detector, "_call_llm", return_value='{"persona": "FRUSTRATED_USER", "confidence": 0.75, "reasoning": "Locked account"}'):
            result = detector.classify(msg, history=[])
            assert hasattr(result, "persona")
            assert hasattr(result, "confidence")
            assert hasattr(result, "reasoning")
            assert result.persona in ["TECHNICAL_EXPERT", "FRUSTRATED_USER", "BUSINESS_EXECUTIVE"]

    def test_confidence_is_between_0_and_1(self, detector):
        msg = "How do I reset my password?"
        with patch.object(detector, "_call_llm", return_value='{"persona": "FRUSTRATED_USER", "confidence": 0.80, "reasoning": "Standard password query"}'):
            result = detector.classify(msg, history=[])
            assert 0.0 <= result.confidence <= 1.0

    def test_keyword_fallback_activates_on_llm_failure(self, detector, monkeypatch):
        # Force LLM failure
        monkeypatch.setattr(detector, "_call_llm", lambda *a, **kw: None)
        result = detector.classify("api token 401 error debug logs", history=[])
        assert result.persona == "TECHNICAL_EXPERT"
