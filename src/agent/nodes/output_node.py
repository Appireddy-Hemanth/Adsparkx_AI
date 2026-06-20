from src.agent.state import AgentState
from src.utils.gemini_client import RateLimitedGeminiClient

async def output_formatting_node(state: AgentState) -> dict:
    messages = list(state.get("messages", []))
    raw_response = state.get("response", "")
    
    # 1. Format the final output layout
    persona = state.get("persona", "UNKNOWN")
    persona_conf = state.get("persona_confidence", 0.0)
    retrieval_conf = state.get("retrieval_confidence", 0.0)
    chunks = state.get("retrieved_chunks", [])
    escalate = state.get("escalate", False)

    # Persona Badge
    emoji = "👤"
    if persona == "TECHNICAL_EXPERT":
        emoji = "🔧"
    elif persona == "FRUSTRATED_USER":
        emoji = "😤"
    elif persona == "BUSINESS_EXECUTIVE":
        emoji = "💼"
    
    persona_spaced = persona.replace("_", " ")
    persona_badge = f"{emoji} {persona_spaced} ({int(persona_conf * 100)}%)"

    # Retrieved Sources
    sources_set = set()
    for chunk in chunks:
        source = chunk.get("source")
        if source:
            sources_set.add(source)
            
    if sources_set:
        sources_str = "\n".join(f"* {src}" for src in sorted(sources_set))
    else:
        sources_str = "None"

    # Escalation Status
    escalation_status = "Triggered" if escalate else "Not Triggered"
    # Determine confidence band
    if retrieval_conf >= 0.75:
        band = "HIGH"
    elif retrieval_conf >= 0.50:
        band = "MEDIUM"
    else:
        band = "LOW"

    # Assemble layout
    formatted_response = (
        f"{persona_badge}\n\n"
        f"Confidence: {retrieval_conf:.2f} ({band})\n\n"
        f"Retrieved Sources:\n{sources_str}\n\n"
        f"Response:\n{raw_response}\n\n"
        f"Escalation:\n{escalation_status}"
    )

    # Append clean response to history if not already appended
    if raw_response and (not messages or messages[-1].get("role") != "assistant" or messages[-1].get("content") != raw_response):
        messages.append({
            "role": "assistant",
            "content": raw_response,
            "persona": persona,
            "persona_confidence": persona_conf,
            "retrieved_chunks": chunks
        })

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
        "response": raw_response,
        "gemini_daily_calls": total_calls,
        "rate_limit_warning": rate_limit_warning
    }
