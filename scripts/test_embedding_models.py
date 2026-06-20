import os
from src.config.settings import settings
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Test list of potential model names
models_to_test = ["text-embedding-004", "models/text-embedding-004", "embedding-001"]

for model_name in models_to_test:
    print(f"Testing embedding model: '{model_name}'...")
    try:
        embeddings = GoogleGenerativeAIEmbeddings(
            model=model_name,
            google_api_key=settings.gemini_api_key,
            task_type="RETRIEVAL_DOCUMENT"
        )
        res = embeddings.embed_query("Hello world")
        print(f"Success! Embedded length: {len(res)}\n")
        break
    except Exception as e:
        print(f"Failed: {e}\n")
