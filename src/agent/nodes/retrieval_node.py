from src.config.settings import settings
from src.rag.retriever import KBRetriever
from src.agent.state import AgentState

def retrieval_node(state: AgentState) -> dict:
    current_message = state.get("current_message", "")
    
    retriever = KBRetriever()
    chunks = retriever.retrieve(current_message, top_k=settings.top_k_retrieval)
    
    chunks_list = []
    if chunks:
        for chunk in chunks:
            chunks_list.append({
                "text": chunk.text,
                "source": chunk.metadata.get("source", "unknown"),
                "section": chunk.metadata.get("section", "General"),
                "page": chunk.metadata.get("page", 1),
                "doc_type": chunk.metadata.get("doc_type", "article"),
                "score": chunk.score,
                "confidence_band": getattr(chunk, "confidence_band", "LOW")
            })
            
    return {
        "retrieved_chunks": chunks_list
    }
