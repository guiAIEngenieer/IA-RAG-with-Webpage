from app.rag import retriever


def test_build_retriever_usa_kwargs():
    chamado = {}

    class FakeVectorStore:
        def as_retriever(self, search_kwargs):
            chamado["search_kwargs"] = search_kwargs
            return "retriever"

    retorno = retriever.build_retriever(FakeVectorStore())

    assert retorno == "retriever"
    assert chamado["search_kwargs"] == {"k": retriever.KWARGS}
