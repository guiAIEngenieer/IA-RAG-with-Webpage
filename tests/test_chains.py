import pytest
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableLambda

from app.rag import chains


def test_build_chain_retorna_chain(monkeypatch):
    class FakeDoc:
        def __init__(self, text):
            self.page_content = text

    class FakeVectorStore:
        def as_retriever(self, search_kwargs):
            return RunnableLambda(lambda _: [FakeDoc("contexto")])

    fake_llm = RunnableLambda(lambda _: AIMessage(content="resposta"))
    monkeypatch.setattr(chains, "get_chat_model", lambda: fake_llm)

    chain = chains.build_chain(FakeVectorStore())

    assert chain is not None
    assert hasattr(chain, "invoke")
    resposta = chain.invoke({"query": "teste", "chat_history": []})
    assert isinstance(resposta, str)


def test_build_chain_relanca_excecao(monkeypatch):
    monkeypatch.setattr(
        chains,
        "build_retriever",
        lambda _: (_ for _ in ()).throw(RuntimeError("erro")),
    )

    with pytest.raises(RuntimeError):
        chains.build_chain(object())
