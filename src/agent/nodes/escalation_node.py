from src.escalation.triggers import EscalationChecker
from src.escalation.handoff import HandoffBuilder
from src.agent.state import AgentState
from src.utils.logger import logger

_escalation_checker_instance = None

async def escalation_evaluation_node(state: AgentState) -> dict:
    global _escalation_checker_instance
    if _escalation_checker_instance is None:
        _escalation_checker_instance = EscalationChecker()
    checker = _escalation_checker_instance
    
    retrieval_confidence = state.get("retrieval_confidence", 0.0)
    current_message = state.get("current_message", "")
    turn_count = state.get("turn_count", 0)
    sentiment_scores = state.get("sentiment_scores", [0.0])
    resolution_attempts = state.get("resolution_attempts", 0)
    response_text = state.get("response", "")

    # Run check
    escalate = state.get("escalate", False) or checker.should_escalate(
        retrieval_confidence=retrieval_confidence,
        user_message=current_message,
        turn_count=turn_count,
        sentiment_scores=sentiment_scores,
        resolution_attempts=resolution_attempts,
        response_text=response_text
    )

    reason = state.get("escalation_reason", "")
    if escalate and not reason:
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

    logger.info(
        f"[ESCALATION] Session={state.get('session_id')} | Escalate={escalate} | "
        f"Reason={reason} | Confidence={retrieval_confidence:.2f} | "
        f"Sentiment={sentiment_scores[-1] if sentiment_scores else 0.0:.2f} | "
        f"Attempts={resolution_attempts}"
    )

    return {
        "escalate": escalate,
        "escalation_reason": reason
    }

_handoff_builder_instance = None

async def human_handoff_node(state: AgentState) -> dict:
    # Only perform handoff if escalation is required
    if not state.get("escalate", False):
        return {}

    global _handoff_builder_instance
    if _handoff_builder_instance is None:
        _handoff_builder_instance = HandoffBuilder()
    builder = _handoff_builder_instance
    
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

    logger.info(f"[HANDOFF] Escalation summary built for Session={state.get('session_id')} with Priority={summary.get('priority')}")

    return {
        "handoff_summary": summary,
        "response": response
    }
