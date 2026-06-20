from src.escalation.triggers import EscalationChecker
from src.escalation.handoff import HandoffBuilder
from src.agent.state import AgentState

def escalation_check_node(state: AgentState) -> dict:
    checker = EscalationChecker()
    
    retrieval_confidence = state.get("retrieval_confidence", 0.0)
    current_message = state.get("current_message", "")
    turn_count = state.get("turn_count", 0)
    sentiment_scores = state.get("sentiment_scores", [0.0])
    resolution_attempts = state.get("resolution_attempts", 0)
    response_text = state.get("response", "")

    # Run check
    escalate = checker.should_escalate(
        retrieval_confidence=retrieval_confidence,
        user_message=current_message,
        turn_count=turn_count,
        sentiment_scores=sentiment_scores,
        resolution_attempts=resolution_attempts,
        response_text=response_text
    )

    reason = ""
    if escalate:
        # Determine main reason for logging/handoff
        if retrieval_confidence < checker.settings.low_confidence_threshold:
            reason = "low_retrieval_confidence"
        elif any(kw in current_message.lower() for kw in checker.sensitive_keywords):
            reason = "sensitive_keyword_triggered"
        elif any(phrase in current_message.lower() for phrase in checker.dissatisfied_phrases):
            reason = "dissatisfied_phrase_triggered"
        elif turn_count >= checker.settings.max_turns_before_review:
            reason = "max_turns_exceeded_with_negative_sentiment"
        elif resolution_attempts >= checker.settings.max_resolution_attempts:
            reason = "max_resolution_attempts_exceeded"
        else:
            reason = "llm_insufficient_information"

    return {
        "escalate": escalate,
        "escalation_reason": reason
    }

def escalation_node(state: AgentState) -> dict:
    builder = HandoffBuilder()
    
    # Build HandoffSummary JSON
    summary = builder.build(
        persona=state.get("persona", "FRUSTRATED_USER"),
        persona_confidence=state.get("persona_confidence", 0.5),
        messages=state.get("messages", []),
        retrieved_chunks=state.get("retrieved_chunks", []),
        attempted_steps=state.get("attempted_steps", []),
        sentiment_scores=state.get("sentiment_scores", [0.0]),
        escalation_reason=state.get("escalation_reason", "Escalation triggered"),
        session_id=state.get("session_id")
    )

    # Set response to a friendly message for user
    response = "I have escalated your request to a human support agent. They will review the handoff summary and contact you shortly."

    return {
        "handoff_summary": summary,
        "response": response
    }
