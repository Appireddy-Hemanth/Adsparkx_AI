# Use the official Python 3.11 slim image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /code

# Copy the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Expose port 7860 (Hugging Face Spaces default port)
EXPOSE 7860

# Run the ingestion script to build the knowledge base, then start Streamlit
CMD ["sh", "-c", "python scripts/ingest_kb.py && streamlit run ui/streamlit_app.py --server.port 7860 --server.address 0.0.0.0"]
