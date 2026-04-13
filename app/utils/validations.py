from urllib.parse import urlparse

from app.config.constants import MAX, MIN


def validate_prompt(text: str) -> str | None:
    if not text:
        return "Invalid prompt."

    if len(text) < MIN:
        return "Prompt too short."

    if len(text) > MAX:
        return "Prompt too long."

    return None


def validate_source_url(url: str) -> str:
    """Returns normalized URL or raises ValueError."""
    u = (url or "").strip()
    if not u:
        raise ValueError("URL cannot be empty.")
    parsed = urlparse(u)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL must use http:// or https://.")
    if not parsed.netloc:
        raise ValueError("Invalid URL: missing host.")
    return u.rstrip("/") or u
