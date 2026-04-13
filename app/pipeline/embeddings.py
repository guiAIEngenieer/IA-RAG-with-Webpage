from langchain_google_genai import GoogleGenerativeAIEmbeddings

from app.config.constants import MODEL_EMBEDDINGS_GENAI


def genai_embedding() -> GoogleGenerativeAIEmbeddings:
    from app.settings import GEMINI_API_KEY

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not defined.")
    return GoogleGenerativeAIEmbeddings(
        model=MODEL_EMBEDDINGS_GENAI,
        google_api_key=GEMINI_API_KEY,
    )
