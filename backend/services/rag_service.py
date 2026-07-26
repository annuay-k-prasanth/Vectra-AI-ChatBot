import os
import tempfile
from typing import Optional

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

CHROMA_DIR = os.path.join(
    BASE_DIR,
    "database",
    "chroma",
)

os.makedirs(CHROMA_DIR, exist_ok=True)

# ============================================================
# EMBEDDING MODEL
# ============================================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# ============================================================
# CHROMA CLIENT
# ============================================================


def get_vector_store(thread_id: str) -> Chroma:
    """
    Returns the Chroma collection for a chat thread.
    Each thread owns one collection.
    """

    return Chroma(
        collection_name=f"thread_{thread_id}",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR,
    )


# ============================================================
# INGEST PDF
# ============================================================


def ingest_pdf(file_bytes: bytes,thread_id: str,filename: Optional[str] = None,) -> dict:
    """
    Read a PDF, split it into chunks,
    embed it and store inside ChromaDB.
    """

    if not file_bytes:
        raise ValueError("No PDF bytes received.")

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".pdf",
    ) as temp:

        temp.write(file_bytes)
        temp_path = temp.name

    try:

        loader = PyPDFLoader(temp_path)

        documents = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n","\n"," ","",],
        )

        chunks = splitter.split_documents(documents)

        for chunk in chunks:

            chunk.metadata["thread_id"] = thread_id
            chunk.metadata["filename"] = (
                filename
                or os.path.basename(temp_path)
            )

        vector_store = get_vector_store(thread_id)

        vector_store.add_documents(chunks)

        return {
            "filename": filename
            or os.path.basename(temp_path),
            "documents": len(documents),
            "chunks": len(chunks),
        }

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)


# ============================================================
# RETRIEVAL
# ============================================================


def rag_search(query: str,thread_id: str,k: int = 4,) -> dict:
    """
    Retrieve relevant chunks from the thread collection.
    """

    vector_store = get_vector_store(thread_id)

    results = vector_store.similarity_search(
        query=query,
        k=k,
    )

    if not results:

        return {
            "query": query,
            "context": [],
            "metadata": [],
            "source_file": None,
        }

    context = [
        doc.page_content
        for doc in results
    ]

    metadata = [
        doc.metadata
        for doc in results
    ]

    filename = None

    if metadata:

        filename = metadata[0].get("filename")

    return {

        "query": query,

        "context": context,

        "metadata": metadata,

        "source_file": filename,
    }


# ============================================================
# HELPERS
# ============================================================


def thread_has_document(thread_id: str,) -> bool:
    """
    Returns True if a thread contains indexed documents.
    """

    vector_store = get_vector_store(thread_id)

    data = vector_store.get()

    ids = data.get("ids", [])

    return len(ids) > 0


def thread_document_metadata(thread_id: str,) -> dict:
    """
    Returns metadata for the first stored document.
    """

    vector_store = get_vector_store(thread_id)

    data = vector_store.get()

    metadata = data.get("metadatas", [])

    if not metadata:

        return {}

    return metadata[0]