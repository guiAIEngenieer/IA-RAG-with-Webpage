import os

from dotenv import load_dotenv

from app.core.logger import logger

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
URL = os.getenv("URL")


def get_required_settings() -> tuple[str, str]:
    if not GEMINI_API_KEY:
        logger.error("ERROR: GEMINI_API_KEY is not defined.")
        raise ValueError("GEMINI_API_KEY is not defined.")

    if not URL or not URL.strip():
        logger.error("ERROR: The website URL is not defined.")
        raise ValueError("URL is not defined.")

    return GEMINI_API_KEY, URL.strip()
