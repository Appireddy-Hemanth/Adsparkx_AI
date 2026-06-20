import re
from src.config.settings import settings
from src.sentiment.analyzer import SentimentAnalyzer

class EscalationChecker:
    def __init__(self):
        self.settings = settings
        self.analyzer = SentimentAnalyzer()
        
        self.sensitive_keywords = [
            "legal", "lawsuit", "lawyer", "refund", "charge dispute",
            "gdpr", "data breach", "account deletion", "fraud", "cancel"
        ]
        self.dissatisfied_phrases = [
            "speak to a human", "real person", "manager", "supervisor",
            "this is unacceptable", "escalate this", "i demand"
        ]

    def should_escalate(
        self,
        retrieval_confidence: float,
        user_message: str,
        turn_count: int,
        sentiment_scores: list[float],
        resolution_attempts: int,
        response_text: str = None
    ) -> bool:
        # 1. Low retrieval confidence
        if retrieval_confidence < self.settings.low_confidence_threshold:
            return True

        # Convert user message to lowercase for matching
        msg_lower = user_message.lower()

        # 2. Sensitive keywords check
        for kw in self.sensitive_keywords:
            if kw in msg_lower:
                return True

        # 3. Dissatisfied phrases check
        for phrase in self.dissatisfied_phrases:
            if phrase in msg_lower:
                return True

        # 4. Turn count threshold + average sentiment threshold
        if turn_count >= self.settings.max_turns_before_review:
            if sentiment_scores:
                avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                if avg_sentiment < self.settings.negative_sentiment_threshold:
                    return True

        # 5. Resolution attempts exceeded + declining sentiment trend
        if resolution_attempts >= self.settings.max_resolution_attempts:
            trend = self.analyzer.sentiment_trend(sentiment_scores)
            if trend == "declining" or (sentiment_scores and sentiment_scores[-1] < self.settings.negative_sentiment_threshold):
                return True

        # 6. LLM response indicates insufficient information
        if response_text and "I don't have enough information" in response_text:
            return True

        return False
