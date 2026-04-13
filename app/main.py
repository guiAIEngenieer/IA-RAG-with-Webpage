"""Ponto de entrada CLI — IA RAG with Webpage (RAG por terminal)."""

from langchain_core.messages import AIMessage, HumanMessage

from app.core.logger import logger
from app.pipeline.ingest import run_ingest
from app.rag.chains import build_chain
from app.settings import get_required_settings
from app.utils.chat_history import truncate_history
from app.utils.validations import validate_prompt

BANNER = """
============================================================
  IA RAG with Webpage
  Fonte: URL definida na variavel de ambiente URL (.env)
============================================================
"""

HELP_TEXT = """Comandos:
  ajuda   - mostra esta ajuda
  url     - mostra a URL da fonte configurada
  limpar  - apaga o historico da conversa
  sair    - encerra o programa

Digite sua pergunta e pressione Enter.
"""


def main() -> None:
    print(BANNER.strip())
    print(HELP_TEXT)

    _, source_url = get_required_settings()
    print(f"Carregando índice / ingest para: {source_url}\n")
    vectorstore = run_ingest(source_url)
    chain = build_chain(vectorstore)
    chat_history: list = []

    print("Pronto. Digite 'ajuda' para ver os comandos.\n")

    while True:
        try:
            query = input("rag> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando.")
            break

        if not query:
            continue

        lowered = query.lower()

        if lowered == "sair":
            print("Até logo.")
            break

        if lowered == "limpar":
            chat_history = []
            logger.info("Chat history cleared.")
            print("(Histórico limpo.)\n")
            continue

        if lowered == "ajuda":
            print(HELP_TEXT)
            continue

        if lowered == "url":
            print(f"URL da fonte: {source_url}\n")
            continue

        error = validate_prompt(query)
        if error:
            logger.error(error)
            print(f"! {error}\n")
            continue

        try:
            response = chain.invoke(
                {"query": query, "chat_history": list(chat_history)}
            )
        except Exception:
            logger.exception("ERROR: RAG chain failed to generate a response.")
            print("! Não foi possível gerar a resposta. Veja os logs para detalhes.\n")
            continue

        chat_history.append(HumanMessage(content=query))
        chat_history.append(AIMessage(content=response))
        chat_history = truncate_history(chat_history)

        logger.info(f"Model response generated (length: {len(response)})")
        print(f"\n{response}\n")


if __name__ == "__main__":
    main()
