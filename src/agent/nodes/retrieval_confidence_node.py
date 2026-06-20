from src.agent.state import AgentState

async def retrieval_confidence_node(state: AgentState) -> dict:
    chunks = state.get("retrieved_chunks", [])
    
    retrieval_confidence = 0.0
    if chunks:
        # The top chunk score defines our retrieval confidence
        retrieval_confidence = chunks[0].get("score", 0.0)
        
    return {
        "retrieval_confidence": retrieval_confidence
    }
