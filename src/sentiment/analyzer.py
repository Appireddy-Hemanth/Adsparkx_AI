from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()

    def analyze(self, text: str) -> dict:
        """Returns {'neg': float, 'neu': float, 'pos': float, 'compound': float}"""
        return self.analyzer.polarity_scores(text)

    def sentiment_trend(self, scores: list[float]) -> str:
        """Returns 'improving' | 'stable' | 'declining' based on scores."""
        if len(scores) < 2:
            return "stable"
        
        # If we have 3 or more scores, compare the last with the third-to-last
        if len(scores) >= 3:
            diff = scores[-1] - scores[-3]
        else:
            diff = scores[-1] - scores[-2]

        if diff < -0.15:
            return "declining"
        elif diff > 0.15:
            return "improving"
        else:
            return "stable"
