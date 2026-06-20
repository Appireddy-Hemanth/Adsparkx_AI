from src.sentiment.analyzer import SentimentAnalyzer
from src.agent.state import AgentState
from src.utils.logger import logger

_sentiment_analyzer_instance = None

def sentiment_node(state: AgentState) -> dict:
    global _sentiment_analyzer_instance
    current_message = state.get("current_message", "")
    sentiment_scores = list(state.get("sentiment_scores", []))
    
    if _sentiment_analyzer_instance is None:
        _sentiment_analyzer_instance = SentimentAnalyzer()
    analyzer = _sentiment_analyzer_instance
    
    sentiment_res = analyzer.analyze(current_message)
    compound_score = sentiment_res.get("compound", 0.0)
    sentiment_scores.append(compound_score)
    
    logger.info(
        f"[SENTIMENT] Session={state.get('session_id')} | Msg='{current_message[:30]}...' | "
        f"Compound={compound_score:.2f} (pos={sentiment_res.get('pos'):.2f}, neg={sentiment_res.get('neg'):.2f})"
    )
    
    return {
        "sentiment_scores": sentiment_scores
    }
