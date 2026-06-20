from src.agent.state import AgentState
from src.utils.gemini_client import RateLimitedGeminiClient

def output_node(state: AgentState) -> dict:
    messages = list(state.get("messages", []))
    response = state.get("response", "")
    
    # Append response to history if not already appended
    if response and (not messages or messages[-1].get("role") != "assistant" or messages[-1].get("content") != response):
        messages.append({"role": "assistant", "content": response})

    # Track daily call counts for rate limits
    total_calls = 0
    for model_name in RateLimitedGeminiClient._shared_daily_counts:
        total_calls += RateLimitedGeminiClient._shared_daily_counts[model_name]
        
    rate_limit_warning = False
    # Threshold for warning is 80% of daily quota (1500 calls) -> 1200 calls
    if total_calls >= 1200:
        rate_limit_warning = True

    return {
        "messages": messages,
        "gemini_daily_calls": total_calls,
        "rate_limit_warning": rate_limit_warning
    }
