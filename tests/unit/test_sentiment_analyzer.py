import pytest
from src.sentiment.analyzer import SentimentAnalyzer

@pytest.fixture
def analyzer():
    return SentimentAnalyzer()

class TestSentimentAnalyzer:

    def test_positive_message_returns_positive_score(self, analyzer):
        score = analyzer.analyze("Thank you, this is very helpful!")
        assert score["compound"] > 0.2

    def test_negative_message_returns_negative_score(self, analyzer):
        score = analyzer.analyze("This is terrible, nothing works, I'm furious!!!")
        assert score["compound"] < -0.2

    def test_neutral_message_returns_near_zero(self, analyzer):
        score = analyzer.analyze("How do I reset my password?")
        assert -0.2 <= score["compound"] <= 0.2

    def test_declining_trend_detected(self, analyzer):
        scores = [-0.1, -0.4, -0.7]
        assert analyzer.sentiment_trend(scores) == "declining"

    def test_improving_trend_detected(self, analyzer):
        scores = [-0.5, -0.2, 0.1]
        assert analyzer.sentiment_trend(scores) == "improving"

    def test_stable_trend_detected(self, analyzer):
        scores = [0.1, 0.05, 0.15]
        assert analyzer.sentiment_trend(scores) == "stable"
