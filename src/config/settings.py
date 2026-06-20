import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    gemini_api_key: str = Field(..., validation_alias="GEMINI_API_KEY")
    gemini_flash_model: str = Field("gemini-2.5-flash", validation_alias="GEMINI_FLASH_MODEL")
    gemini_lite_model: str = Field("gemini-2.5-flash-lite", validation_alias="GEMINI_LITE_MODEL")
    gemini_embedding_model: str = Field("models/text-embedding-004", validation_alias="GEMINI_EMBEDDING_MODEL")
    
    chroma_persist_dir: str = Field("./chroma_db", validation_alias="CHROMA_PERSIST_DIR")
    chroma_collection: str = Field("novasuite_support_kb", validation_alias="CHROMA_COLLECTION")
    top_k_retrieval: int = Field(5, validation_alias="TOP_K_RETRIEVAL")
    
    low_confidence_threshold: float = Field(0.50, validation_alias="LOW_CONFIDENCE_THRESHOLD")
    negative_sentiment_threshold: float = Field(-0.40, validation_alias="NEGATIVE_SENTIMENT_THRESHOLD")
    max_turns_before_review: int = Field(5, validation_alias="MAX_TURNS_BEFORE_REVIEW")
    max_resolution_attempts: int = Field(3, validation_alias="MAX_RESOLUTION_ATTEMPTS")
    
    kb_data_dir: str = Field("./data", validation_alias="KB_DATA_DIR")
    log_level: str = Field("INFO", validation_alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Load settings singleton
settings = Settings()
