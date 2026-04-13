from langchain_classic.evaluation.qa import QAEvalChain, QAGenerateChain

from app.core.logger import logger
from app.rag.llms import get_chat_model


def evaluate(querys_answers, generations):
    if not querys_answers or not generations:
        raise ValueError("querys_answers and generations must not be empty.")

    eval_chain = QAEvalChain.from_llm(get_chat_model())
    return eval_chain.evaluate(querys_answers, generations)


def defining_pairs(chunks):
    if not chunks:
        raise ValueError("chunks must not be empty.")

    qa_chain = QAGenerateChain.from_llm(get_chat_model())

    try:
        pairs = qa_chain.apply_and_parse(
            [{"page": p.page_content} for p in chunks]
        )
    except Exception:
        logger.exception(
            "ERROR: Failed to generate Q/A pairs from chunks "
            "(app/utils/evaluation.py/defining_pairs)."
        )
        raise

    return querys_answers_generations(pairs)


def querys_answers_generations(pairs):
    if not pairs:
        raise ValueError("pairs must not be empty.")

    generations = []
    querys_answers = [pair["qa_pairs"] for pair in pairs]
    llm = get_chat_model()

    for qa in querys_answers:
        if "query" not in qa:
            raise KeyError("Each qa_pairs item must include 'query'.")
        response = llm.invoke(qa["query"])
        generations.append(
            {"result": getattr(response, "content", str(response))}
        )

    return evaluate(querys_answers, generations)
