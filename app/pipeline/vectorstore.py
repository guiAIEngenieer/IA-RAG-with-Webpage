import hashlib
import os

import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS

from app.config.constants import FAISS_BASE, NEIGHBORS
from app.core.logger import logger
from app.pipeline.embeddings import genai_embedding


def faiss_path_for_url(url: str) -> str:
    """Stable directory path for a normalized source URL (one index per URL)."""
    normalized = (url or "").strip().rstrip("/")
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()
    return os.path.join(FAISS_BASE, digest)


def load_vectorstore_if_exists(*, url: str):
    path = faiss_path_for_url(url)
    if not os.path.isdir(path):
        return None

    try:
        return FAISS.load_local(
            path,
            genai_embedding(),
            allow_dangerous_deserialization=True,
        )
    except Exception:
        logger.exception(
            "ERROR: Failed to load FAISS index (%s).",
            path,
        )
        return None


def build_faiss(chunks, *, url: str):
    if not chunks:
        logger.error("ERROR: No chunks received for indexing.")
        raise ValueError("No chunks to index.")

    path = faiss_path_for_url(url)
    os.makedirs(path, exist_ok=True)

    try:
        embedding_model = genai_embedding()
        sample_vector = embedding_model.embed_query("dimension_probe")
        vector_dim = len(sample_vector)

        index = faiss.IndexHNSWFlat(vector_dim, NEIGHBORS)

        vectorstore = FAISS(
            embedding_function=embedding_model,
            index=index,
            docstore=InMemoryDocstore({}),
            index_to_docstore_id={},
        )
        vectorstore.add_documents(chunks)
        vectorstore.save_local(path)

        return vectorstore

    except Exception:
        logger.exception(
            "ERROR: Failed to create FAISS index at %s.",
            path,
        )
        raise


def get_or_create_vectorstore(chunks, *, url: str):
    existing = load_vectorstore_if_exists(url=url)
    if existing is not None:
        return existing
    return build_faiss(chunks, url=url)
