from src.personas.detector import PersonaDetector
from src.agent.state import AgentState
from src.utils.logger import logger

_persona_detector_instance = None

def persona_node(state: AgentState) -> dict:
    global _persona_detector_instance
    current_message = state.get("current_message", "")
    history = state.get("messages", [])[:-1]  # Exclude the current message
    
    if _persona_detector_instance is None:
        _persona_detector_instance = PersonaDetector()
    detector = _persona_detector_instance
    
    result = detector.classify(current_message, history=history)
    
    logger.info(
        f"[PERSONA] Session={state.get('session_id')} | Msg='{current_message[:30]}...' | "
        f"Detected={result.persona} (conf={result.confidence:.2f}) | Reasoning='{result.reasoning}'"
    )
    
    return {
        "persona": result.persona,
        "persona_confidence": result.confidence
    }
