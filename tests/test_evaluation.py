from app.utils import evaluation
import pytest


def test_evaluate_chama_chain(monkeypatch):
    esperado = [{"grade": "CORRECT"}]

    class FakeEvalChain:
        def evaluate(self, querys_answers, generations):
            assert querys_answers == [{"query": "q", "answer": "a"}]
            assert generations == [{"result": "r"}]
            return esperado

    class FakeQAEvalChain:
        @staticmethod
        def from_llm(_):
            return FakeEvalChain()

    monkeypatch.setattr(evaluation, "QAEvalChain", FakeQAEvalChain)

    retorno = evaluation.evaluate([{"query": "q", "answer": "a"}], [{"result": "r"}])
    assert retorno == esperado


def test_querys_answers_generations_monta_resultado(monkeypatch):
    monkeypatch.setattr(evaluation, "evaluate", lambda qa, gen: {"qa": qa, "gen": gen})

    class FakeResponse:
        content = "resp:pergunta"

    fake_llm = type("LLM", (), {"invoke": staticmethod(lambda q: FakeResponse())})()
    monkeypatch.setattr(evaluation, "get_chat_model", lambda: fake_llm)

    pairs = [{"qa_pairs": {"query": "pergunta", "answer": "resposta"}}]
    retorno = evaluation.querys_answers_generations(pairs)

    assert retorno == {
        "qa": [{"query": "pergunta", "answer": "resposta"}],
        "gen": [{"result": "resp:pergunta"}],
    }


def test_querys_answers_generations_com_string_retorna_texto(monkeypatch):
    monkeypatch.setattr(evaluation, "evaluate", lambda qa, gen: {"qa": qa, "gen": gen})
    fake_llm = type("LLM", (), {"invoke": staticmethod(lambda q: f"resp:{q}")})()
    monkeypatch.setattr(evaluation, "get_chat_model", lambda: fake_llm)

    pairs = [{"qa_pairs": {"query": "abc", "answer": "ok"}}]
    retorno = evaluation.querys_answers_generations(pairs)
    assert retorno["gen"] == [{"result": "resp:abc"}]


def test_defining_pairs_chama_gerador(monkeypatch):
    class FakeGenerateChain:
        def apply_and_parse(self, pages):
            assert pages == [{"page": "bloco"}]
            return [{"qa_pairs": {"query": "q", "answer": "a"}}]

    class FakeQAGenerateChain:
        @staticmethod
        def from_llm(_):
            return FakeGenerateChain()

    monkeypatch.setattr(evaluation, "QAGenerateChain", FakeQAGenerateChain)
    monkeypatch.setattr(evaluation, "get_chat_model", lambda: object())
    monkeypatch.setattr(evaluation, "querys_answers_generations", lambda pairs: {"ok": pairs})

    chunk = type("Chunk", (), {"page_content": "bloco"})
    retorno = evaluation.defining_pairs([chunk])

    assert retorno == {"ok": [{"qa_pairs": {"query": "q", "answer": "a"}}]}


def test_evaluate_quando_listas_vazias():
    with pytest.raises(ValueError):
        evaluation.evaluate([], [])


def test_defining_pairs_quando_chunks_vazio():
    with pytest.raises(ValueError):
        evaluation.defining_pairs([])


def test_querys_answers_generations_quando_pairs_vazio():
    with pytest.raises(ValueError):
        evaluation.querys_answers_generations([])


def test_querys_answers_generations_sem_query():
    with pytest.raises(KeyError):
        evaluation.querys_answers_generations([{"qa_pairs": {"answer": "x"}}])
