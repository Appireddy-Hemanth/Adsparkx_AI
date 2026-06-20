from src.personas.detector import PersonaDetector
from src.agent.state import AgentState

def persona_node(state: AgentState) -> dict:
    current_message = state.get("current_message", "")
    history = state.get("messages", [])[:-1]  # Exclude the current message to match history signature if desired, or pass all
    
    detector = PersonaDetector()
    result = detector.classify(current_message, history=history)
    
    return {
        "persona": result.persona,
        "persona_confidence": result.confidence
    }
