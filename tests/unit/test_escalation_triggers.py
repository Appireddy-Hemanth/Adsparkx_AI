import pytest
from src.escalation.triggers import EscalationChecker

@pytest.fixture
def checker():
    return EscalationChecker()

class TestEscalationTriggers:

    def test_low_confidence_triggers_escalation(self, checker):
        assert checker.should_escalate(
            retrieval_confidence=0.30,
            user_message="random question",
            turn_count=1,
            sentiment_scores=[0.0],
            resolution_attempts=0
        ) is True

    def test_sensitive_keyword_triggers_escalation(self, checker):
        assert checker.should_escalate(
            retrieval_confidence=0.90,
            user_message="I want to speak to a lawyer about this",
            turn_count=1,
            sentiment_scores=[0.0],
            resolution_attempts=0
        ) is True

    def test_dissatisfied_phrase_triggers_escalation(self, checker):
        assert checker.should_escalate(
            retrieval_confidence=0.90,
            user_message="I want to speak to a manager right now",
            turn_count=2,
            sentiment_scores=[-0.5, -0.6],
            resolution_attempts=1
        ) is True

    def test_normal_query_does_not_escalate(self, checker):
        assert checker.should_escalate(
            retrieval_confidence=0.85,
            user_message="How do I reset my password?",
            turn_count=1,
            sentiment_scores=[0.1],
            resolution_attempts=0
        ) is False

    def test_max_attempts_exceeded_triggers_escalation(self, checker):
        assert checker.should_escalate(
            retrieval_confidence=0.80,
            user_message="Still not working",
            turn_count=6,
            sentiment_scores=[-0.3, -0.5, -0.6],
            resolution_attempts=4
        ) is True
