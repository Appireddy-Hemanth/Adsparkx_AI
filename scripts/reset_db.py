import os
import shutil
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.config.settings import settings
from src.utils.logger import logger
from src.rag.ingestion import ingest_all

def reset_database():
    db_path = settings.chroma_persist_dir
    if os.path.exists(db_path):
        logger.info(f"Wiping existing ChromaDB directory at {db_path}...")
        try:
            # We must be careful to handle files locked by processes
            shutil.rmtree(db_path)
            logger.info("Database wiped successfully.")
        except Exception as e:
            logger.error(f"Failed to wipe database directory: {e}")
            logger.info("Attempting to delete files individually...")
            # Fallback
            for root, dirs, files in os.walk(db_path):
                for f in files:
                    try:
                        os.remove(os.path.join(root, f))
                    except Exception:
                        pass
    else:
        logger.info("No existing database directory found to wipe.")
        
    # Re-run ingestion
    ingest_all()

if __name__ == "__main__":
    try:
        reset_database()
        logger.info("Database reset completed successfully.")
    except Exception as e:
        logger.error(f"Database reset failed: {e}")
        sys.exit(1)
