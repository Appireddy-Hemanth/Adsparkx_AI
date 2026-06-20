import uuid
from src.agent.state import AgentState

async def input_node(state: AgentState) -> dict:
    current_message = state.get("current_message", "").strip()
    
    # Initialize list fields if not present
    messages = list(state.get("messages", []))
    sentiment_scores = list(state.get("sentiment_scores", []))
    attempted_steps = list(state.get("attempted_steps", []))
    session_id = state.get("session_id") or str(uuid.uuid4())
    
    # Add user message to history
    messages.append({"role": "user", "content": current_message})
    
    # Increment turn count
    turn_count = state.get("turn_count", 0) + 1
    
    # Check resolution attempts
    resolution_attempts = state.get("resolution_attempts", 0)
    # If the user says "still not working" or similar, increment resolution attempts
    msg_lower = current_message.lower()
    if "not working" in msg_lower or "tried" in msg_lower or "still" in msg_lower or "fails" in msg_lower:
        resolution_attempts += 1
        
    return {
        "session_id": session_id,
        "current_message": current_message,
        "messages": messages,
        "sentiment_scores": sentiment_scores,
        "attempted_steps": attempted_steps,
        "turn_count": turn_count,
        "resolution_attempts": resolution_attempts,
        "escalate": state.get("escalate", False),
        "escalation_reason": state.get("escalation_reason", "")
    }
