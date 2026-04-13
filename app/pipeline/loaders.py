from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError

from langchain_community.document_loaders import RecursiveUrlLoader, WebBaseLoader

from app.core.logger import logger
from app.utils.validations import validate_source_url


def loader_web(url: str):
    normalized = validate_source_url(url)
    try:
        loader = RecursiveUrlLoader(
            url=normalized,
            max_depth=1,
            continue_on_failure=True,
        )
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(loader.load)
            return future.result(timeout=30)
    except FuturesTimeoutError:
        logger.warning(
            "WARNING: Recursive URL loader timed out; falling back to single-page loader."
        )
        fallback_loader = WebBaseLoader(web_path=normalized)
        return fallback_loader.load()
    except Exception:
        logger.exception(
            "ERROR: Failed to load page (app/pipeline/loaders.py/loader_web)."
        )
        raise
