import os
import hashlib
import chromadb
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config.settings import settings
from src.rag.embeddings import get_embeddings, GeminiChromaEmbeddingFunction
from src.utils.logger import logger

def get_chroma_client():
    return chromadb.PersistentClient(path=settings.chroma_persist_dir)

def get_chroma_collection(client):
    # Retrieve embedding function configured for document retrieval
    emb_model = get_embeddings(task_type="RETRIEVAL_DOCUMENT")
    emb_fn = GeminiChromaEmbeddingFunction(emb_model)
    return client.get_or_create_collection(
        name=settings.chroma_collection,
        embedding_function=emb_fn,
        metadata={"hnsw:space": "cosine"}
    )

def infer_doc_type(filename: str) -> str:
    """Infer doc_type based on filename keyword."""
    filename_lower = filename.lower()
    if "policy" in filename_lower or "sla" in filename_lower:
        return "policy"
    elif "faq" in filename_lower:
        return "faq"
    elif "guide" in filename_lower or "setup" in filename_lower:
        return "guide"
    elif "reference" in filename_lower or "api" in filename_lower:
        return "reference"
    elif "playbook" in filename_lower or "troubleshooting" in filename_lower:
        return "troubleshooting"
    return "article"

def load_documents_from_dir(dir_path: str):
    documents = []
    if not os.path.exists(dir_path):
        logger.warning(f"KB directory {dir_path} does not exist.")
        return documents

    # Walk through directory
    for root, _, files in os.walk(dir_path):
        for file in files:
            file_path = os.path.join(root, file)
            source_name = file
            logger.info(f"Loading document: {file_path}")
            
            try:
                if file.endswith(".pdf"):
                    loader = PyPDFLoader(file_path)
                    docs = loader.load()
                elif file.endswith(".txt"):
                    loader = TextLoader(file_path, encoding="utf-8")
                    docs = loader.load()
                elif file.endswith(".md"):
                    try:
                        loader = UnstructuredMarkdownLoader(file_path)
                        docs = loader.load()
                    except Exception as e:
                        logger.warning(f"UnstructuredMarkdownLoader failed for {file_path}, falling back to TextLoader: {e}")
                        loader = TextLoader(file_path, encoding="utf-8")
                        docs = loader.load()
                else:
                    continue
                
                # Add metadata to loaded documents
                for idx, doc in enumerate(docs):
                    doc.metadata["source"] = source_name
                    doc.metadata["page"] = doc.metadata.get("page", idx + 1)
                    doc.metadata["doc_type"] = infer_doc_type(source_name)
                    # Try to infer section from header or first line
                    first_line = doc.page_content.strip().split("\n")[0]
                    if len(first_line) < 100:
                        doc.metadata["section"] = first_line.lstrip("#").strip()
                    else:
                        doc.metadata["section"] = "General"
                
                documents.extend(docs)
            except Exception as e:
                logger.error(f"Error loading {file_path}: {e}")
                
    return documents

def ingest_all():
    logger.info("Starting ingestion process...")
    # Load all docs
    raw_docs = load_documents_from_dir(settings.kb_data_dir)
    logger.info(f"Loaded {len(raw_docs)} raw documents pages/files.")
    
    if not raw_docs:
        logger.warning("No documents loaded. Ingestion skipped.")
        return
        
    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=64,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    chunks = text_splitter.split_documents(raw_docs)
    logger.info(f"Created {len(chunks)} chunks from raw documents.")

    client = get_chroma_client()
    collection = get_chroma_collection(client)

    ids = []
    documents = []
    metadatas = []

    for idx, chunk in enumerate(chunks):
        content = chunk.page_content
        source = chunk.metadata.get("source", "unknown")
        page = chunk.metadata.get("page", 1)
        doc_type = chunk.metadata.get("doc_type", "article")
        section = chunk.metadata.get("section", "General")

        # Deterministic chunk_id based on source, page, index and content hash
        hash_val = hashlib.md5(content.encode("utf-8")).hexdigest()[:10]
        chunk_id = f"{source.replace('.', '_')}_p{page}_c{idx}_{hash_val}"
        
        ids.append(chunk_id)
        documents.append(content)
        metadatas.append({
            "source": source,
            "page": page,
            "doc_type": doc_type,
            "section": section,
            "chunk_id": chunk_id
        })

    # Upsert in batches of 100 to stay within Limits and avoid overhead
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i+batch_size]
        batch_docs = documents[i:i+batch_size]
        batch_meta = metadatas[i:i+batch_size]
        collection.upsert(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_meta
        )
        logger.info(f"Upserted batch {i//batch_size + 1}/{(len(ids)-1)//batch_size + 1}")

    logger.info("Ingestion completed successfully.")
