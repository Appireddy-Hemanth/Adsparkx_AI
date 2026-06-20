import os
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

class KBRetriever:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        self.emb_model = get_embeddings(task_type="RETRIEVAL_QUERY")
        self.emb_fn = GeminiChromaEmbeddingFunction(self.emb_model)
        
        # Load collection
        try:
            self.collection = self.client.get_collection(
                name=settings.chroma_collection,
                embedding_function=self.emb_fn
            )
        except Exception as e:
            logger.warning(f"Could not load Chroma collection: {e}. It might not be created yet.")
            self.collection = None

        # Lazy load CrossEncoder to minimize startup latency
        self._reranker = None

    @property
    def reranker(self):
        global _HAS_CROSS_ENCODER
        if _HAS_CROSS_ENCODER and self._reranker is None:
            try:
                logger.info("Loading CrossEncoder (cross-encoder/ms-marco-MiniLM-L-6-v2) for reranking...")
                self._reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
            except Exception as e:
                logger.error(f"Failed to load CrossEncoder reranker: {e}. Falling back to default Chroma scores.")
                _HAS_CROSS_ENCODER = False
        return self._reranker

    def retrieve(self, query: str, top_k: int = 5) -> list[RetrievedChunk]:
        if not self.collection:
            # Re-attempt loading collection
            try:
                self.collection = self.client.get_collection(
                    name=settings.chroma_collection,
                    embedding_function=self.emb_fn
                )
            except Exception as e:
                logger.error(f"Failed to load Chroma collection during retrieval: {e}")
                return []

        # 1. Embed query
        # chroma handles this if embedding function is passed, but we can query it directly
        # Query ChromaDB for top_k * 2 candidates (for reranking)
        candidates_to_fetch = top_k * 2 if _HAS_CROSS_ENCODER else top_k
        try:
            results = self.collection.query(
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
        chunks = []
        for doc, meta, dist in zip(documents, metadatas, distances):
            # Chroma cosine distance ranges from 0 (similar) to 2 (dissimilar)
            # Normalise distance score to a 0-1 confidence range
            raw_score = max(0.0, 1.0 - dist)
            chunks.append(RetrievedChunk(text=doc, metadata=meta, score=raw_score))

        # 2. Rerank with Cross-Encoder if available
        if _HAS_CROSS_ENCODER and self.reranker and len(chunks) > 1:
            try:
                pairs = [[query, chunk.text] for chunk in chunks]
                rerank_scores = self.reranker.predict(pairs)
                
                # Pair and sort by rerank score descending
                for chunk, r_score in zip(chunks, rerank_scores):
                    # Sigmoid normalization for cross-encoder logits if they are raw scores
                    # (cross-encoder scores for ms-marco can be negative or positive logits)
                    import math
                    sig_score = 1 / (1 + math.exp(-r_score))
                    chunk.score = sig_score
                
                chunks.sort(key=lambda x: x.score, reverse=True)
            except Exception as e:
                logger.error(f"Error during CrossEncoder reranking: {e}. Keeping raw retrieval order.")
                # Keep raw order but sort by raw score
                chunks.sort(key=lambda x: x.score, reverse=True)

        return chunks[:top_k]
