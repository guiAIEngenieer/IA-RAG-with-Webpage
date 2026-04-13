from langchain_core.documents import Document
from app.config.constants import CHUNK_SIZE, CHUNK_OVERLAP
from app.core.logger import logger

def chunking(webpage):
    try:
        chunks = []
        step = CHUNK_SIZE - CHUNK_OVERLAP

        for doc in webpage:
            text = (doc.page_content or "").strip()
            if not text:
                continue
            metadata = dict(getattr(doc, "metadata", {}) or {})
            for i in range(0, len(text), step):
                piece = text[i:i + CHUNK_SIZE]
                if piece:
                    chunks.append(Document(page_content=piece, metadata=metadata))

        if not chunks:
            raise ValueError("No chunks generated from loaded website content.")
        return chunks
    
    except Exception:
        logger.exception(
            "ERROR: Chunking failed (app/pipeline/chunker.py/chunking)."
        )
        raise