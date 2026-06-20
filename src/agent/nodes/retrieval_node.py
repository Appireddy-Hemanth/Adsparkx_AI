from src.rag.retriever import KBRetriever
from src.agent.state import AgentState

def retrieval_node(state: AgentState) -> dict:
    current_message = state.get("current_message", "")
    
    retriever = KBRetriever()
    chunks = retriever.retrieve(current_message, top_k=5)
    
    # Map to list of dicts for State serialization compatibility
    chunks_list = []
    retrieval_confidence = 0.0
    
    if chunks:
        # The top chunk score defines our retrieval confidence
        retrieval_confidence = chunks[0].score
        for chunk in chunks:
            chunks_list.append({
                "text": chunk.text,
                "source": chunk.metadata.get("source", "unknown"),
                "section": chunk.metadata.get("section", "General"),
                "page": chunk.metadata.get("page", 1),
                "doc_type": chunk.metadata.get("doc_type", "article"),
                "score": chunk.score
            })
            
    return {
        "retrieved_chunks": chunks_list,
        "retrieval_confidence": retrieval_confidence
    }
