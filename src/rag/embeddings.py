from langchain_google_genai import GoogleGenerativeAIEmbeddings
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
from src.config.settings import settings

class GeminiChromaEmbeddingFunction(EmbeddingFunction):
    def __init__(self, embeddings_model):
        self.embeddings_model = embeddings_model

    def __call__(self, input: Documents) -> Embeddings:
        # Chroma expects a list of list of floats
        return self.embeddings_model.embed_documents(input)

def get_embeddings(task_type: str = "RETRIEVAL_DOCUMENT"):
    """
    Returns GoogleGenerativeAIEmbeddings configured for specific task types.
    task_type can be 'RETRIEVAL_DOCUMENT' or 'RETRIEVAL_QUERY'.
    """
    return GoogleGenerativeAIEmbeddings(
        model=settings.gemini_embedding_model,
        google_api_key=settings.gemini_api_key,
        task_type=task_type
    )
