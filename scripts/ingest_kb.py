import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.rag.ingestion import ingest_all
from src.utils.logger import logger
from scripts.generate_kb import generate_sla_pdf

if __name__ == "__main__":
    # Check if kb files exist, if not, generate them
    if not os.path.exists("data") or len(os.listdir("data/txt") if os.path.exists("data/txt") else []) < 4:
        logger.info("Knowledge base files not found. Generating them first...")
        # We can just import and run generate_kb main flow if needed
        # But wait, we can just run the generate_kb script or import its functions
        from scripts import generate_kb
        
    try:
        ingest_all()
        logger.info("Ingestion completed successfully.")
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        sys.exit(1)
