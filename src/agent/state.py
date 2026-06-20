from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict):
    session_id: str
    messages: List[Dict[str, Any]]
    current_message: str
    persona: str
    persona_confidence: float
    retrieved_chunks: List[Dict[str, Any]]
    retrieval_confidence: float
    response: str
    escalate: bool
    escalation_reason: str
    handoff_summary: Optional[Dict[str, Any]]
    turn_count: int
    resolution_attempts: int
    sentiment_scores: List[float]
    attempted_steps: List[str]
    gemini_daily_calls: int          # Track against 1,500 RPD limit
    rate_limit_warning: bool         # True when >80% of daily quota used
    response_time: Optional[float]
