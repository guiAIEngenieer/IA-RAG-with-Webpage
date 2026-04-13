from app.core.logger import logger
from app.utils.validations import validate_source_url

from .chunker import chunking
from .loaders import loader_web
from .vectorstore import get_or_create_vectorstore, load_vectorstore_if_exists


def run_ingest(url: str):
    normalized = validate_source_url(url)
    try:
        logger.info("INFO: Checking FAISS index for current URL.")
        existing_vectorstore = load_vectorstore_if_exists(url=normalized)
        if existing_vectorstore is not None:
            logger.info("INFO: Existing FAISS index loaded; skipping web ingest.")
            return existing_vectorstore

        logger.info("INFO: Starting website load for ingest.")
        page = loader_web(normalized)
        logger.info("INFO: Website loaded. Document count: %s", len(page))
        logger.info("INFO: Starting chunking.")
        chunks = chunking(page)
        logger.info("INFO: Chunking finished. Chunk count: %s", len(chunks))
        logger.info("INFO: Building FAISS index.")
        return get_or_create_vectorstore(chunks, url=normalized)

    except Exception:
        logger.exception(
            "ERROR: Ingest pipeline failed (app/pipeline/ingest.py/run_ingest)."
        )
        raise
