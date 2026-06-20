import os
import asyncio
from dataclasses import dataclass
from src.config.settings import settings
from src.rag.embeddings import get_embeddings, GeminiChromaEmbeddingFunction
from src.utils.logger import logger
import chromadb

# Try to import CrossEncoder for reranking
try:
    from sentence_transformers import CrossEncoder
    _HAS_CROSS_ENCODER = True
except ImportError:
    _HAS_CROSS_ENCODER = False

@dataclass
class RetrievedChunk:
    text: str
    metadata: dict
    score: float  # Relevance score (normalized to 0-1)
    confidence_band: str = "LOW"

_chroma_client = None
_chroma_collection = None
_cross_encoder_instance = None

class KBRetriever:
    def __init__(self):
        global _chroma_client, _chroma_collection
        if _chroma_client is None:
            _chroma_client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.client = _chroma_client
        
        self.emb_model = get_embeddings(task_type="RETRIEVAL_QUERY")
        self.emb_fn = GeminiChromaEmbeddingFunction(self.emb_model)
        
        if _chroma_collection is None:
            try:
                _chroma_collection = self.client.get_collection(
                    name=settings.chroma_collection,
                    embedding_function=self.emb_fn
                )
            except Exception as e:
                logger.warning(f"Could not load Chroma collection: {e}. It might not be created yet.")
                _chroma_collection = None
        self.collection = _chroma_collection

        # Lazy load CrossEncoder to minimize startup latency
        pass

    @property
    def reranker(self):
        global _HAS_CROSS_ENCODER, _cross_encoder_instance
        if _HAS_CROSS_ENCODER and _cross_encoder_instance is None:
            try:
                logger.info("Loading CrossEncoder (cross-encoder/ms-marco-MiniLM-L-6-v2) for reranking...")
                _cross_encoder_instance = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            except Exception as e:
                logger.error(f"Failed to load CrossEncoder reranker: {e}. Falling back to default Chroma scores.")
                _HAS_CROSS_ENCODER = False
        return _cross_encoder_instance

    async def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        global _chroma_collection
        if not self.collection:
            # Re-attempt loading collection
            try:
                _chroma_collection = self.client.get_collection(
                    name=settings.chroma_collection,
                    embedding_function=self.emb_fn
                )
                self.collection = _chroma_collection
            except Exception as e:
                logger.error(f"Failed to load Chroma collection during retrieval: {e}")
                return []

        # 1. Embed query
        # chroma handles this if embedding function is passed, but we can query it directly
        # Query ChromaDB for top_k * 2 candidates (for reranking)
        candidates_to_fetch = top_k * 2 if _HAS_CROSS_ENCODER else top_k
        try:
            results = await asyncio.to_thread(
                self.collection.query,
                query_texts=[query],
                n_results=candidates_to_fetch
            )
        except Exception as e:
            logger.error(f"Error querying ChromaDB: {e}")
            return []

        if not results or not results['documents'] or not results['documents'][0]:
            return []

        documents = results['documents'][0]
        metadatas = results['metadatas'][0]
        distances = results['distances'][0] if 'distances' in results and results['distances'] else [1.0] * len(documents)

        # Map distance to similarity (1 - distance for cosine)
        seen_texts = set()
        chunks = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            # Normalise distance score to a 0-1 confidence range
            score = max(0.0, min(1.0, 1.0 - dist))
            
            # Deduplicate chunks by exact content text
            normalized_text = doc.strip().lower()
            if normalized_text in seen_texts:
                continue
            seen_texts.add(normalized_text)
            
            # Filter low-quality matches (threshold 0.30)
            if score < 0.30:
                continue
                
            chunks.append(RetrievedChunk(text=doc, metadata=meta, score=score))

        # 2. Rerank with Cross-Encoder if available
        if _HAS_CROSS_ENCODER and self.reranker and len(chunks) > 1:
            try:
                pairs = [[query, chunk.text] for chunk in chunks]
                rerank_scores = await asyncio.to_thread(self.reranker.predict, pairs)
                
                # Pair and sort by rerank score descending
                for chunk, r_score in zip(chunks, rerank_scores):
                    # Sigmoid normalization for cross-encoder logits
                    import math
                    sig_score = 1 / (1 + math.exp(-r_score))
                    chunk.score = sig_score
            except Exception as e:
                logger.error(f"Error during CrossEncoder reranking: {e}. Keeping raw retrieval scores.")

        # Compute confidence band for all chunks based on final score
        for chunk in chunks:
            if chunk.score >= 0.75:
                chunk.confidence_band = "HIGH"
            elif chunk.score >= 0.50:
                chunk.confidence_band = "MEDIUM"
            else:
                chunk.confidence_band = "LOW"

        # Ensure chunks are sorted by score descending
        chunks.sort(key=lambda x: x.score, reverse=True)
        return chunks[:top_k]
