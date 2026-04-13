from operator import itemgetter

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

from app.core.logger import logger
from app.rag.llms import get_chat_model
from app.rag.prompts import RAG_PROMPT
from app.rag.retriever import build_retriever


def build_chain(vectorstore):
    try:
        retriever = build_retriever(vectorstore)
        llm = get_chat_model()

        def safe_history(payload):
            return payload.get("chat_history", [])

        def format_context(docs):
            return "\n\n".join(doc.page_content for doc in docs)

        chain = (
            {
                "context": itemgetter("query") | retriever,
                "query": itemgetter("query"),
                "chat_history": RunnableLambda(safe_history),
            }
            | RunnableLambda(
                lambda payload: {
                    "context": format_context(payload["context"]),
                    "query": payload["query"],
                    "chat_history": payload["chat_history"],
                }
            )
            | RAG_PROMPT
            | llm
            | StrOutputParser()
        )

        return chain

    except Exception:
        logger.exception(
            "ERROR: Failed to build RAG chain (app/rag/chains.py/build_chain)."
        )
        raise
