from langchain_google_genai import ChatGoogleGenerativeAI

from app.config.constants import MODEL_GENAI, TEMP_GENAI


def get_chat_model() -> ChatGoogleGenerativeAI:
    """Instância nova a cada chamada para respeitar mudanças de env em testes."""
    from app.settings import GEMINI_API_KEY

    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not defined.")
    return ChatGoogleGenerativeAI(
        model=MODEL_GENAI,
        api_key=GEMINI_API_KEY,
        temperature=TEMP_GENAI,
    )
