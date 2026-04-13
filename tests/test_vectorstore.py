import pytest

from app.config.constants import FAISS_BASE
from app.pipeline import vectorstore


def test_faiss_path_for_url_estavel():
    p1 = vectorstore.faiss_path_for_url("https://example.com/")
    p2 = vectorstore.faiss_path_for_url("https://example.com")
    assert p1 == p2
    assert p1.startswith(FAISS_BASE)


def test_load_vectorstore_if_exists_quando_nao_existe(monkeypatch):
    monkeypatch.setattr(vectorstore.os.path, "isdir", lambda _: False)
    assert vectorstore.load_vectorstore_if_exists(url="https://a.com") is None


def test_load_vectorstore_if_exists_quando_existe(monkeypatch):
    expected_path = vectorstore.faiss_path_for_url("https://x.com")

    class FakeFAISS:
        @staticmethod
        def load_local(path, embedding, allow_dangerous_deserialization):
            assert path == expected_path
            assert embedding == "embedding"
            assert allow_dangerous_deserialization is True
            return "vectorstore"

    monkeypatch.setattr(vectorstore.os.path, "isdir", lambda p: p == expected_path)
    monkeypatch.setattr(vectorstore, "FAISS", FakeFAISS)
    monkeypatch.setattr(vectorstore, "genai_embedding", lambda: "embedding")

    assert vectorstore.load_vectorstore_if_exists(url="https://x.com") == "vectorstore"


def test_build_faiss_sem_chunks():
    with pytest.raises(ValueError, match="No chunks"):
        vectorstore.build_faiss([], url="https://z.com")


def test_build_faiss_com_chunks(monkeypatch):
    index_criado = object()
    docstore_criado = object()
    url = "https://example.com/index"
    expected_path = vectorstore.faiss_path_for_url(url)

    class FakeVectorDB:
        def __init__(self, embedding_function, index, docstore, index_to_docstore_id):
            assert hasattr(embedding_function, "embed_query")
            assert index is index_criado
            assert docstore is docstore_criado
            assert index_to_docstore_id == {}
            self.saved_path = None
            self.docs = None

        def add_documents(self, chunks):
            self.docs = chunks

        def save_local(self, path):
            self.saved_path = path

    class FakeFAISS:
        def __new__(cls, **kwargs):
            return FakeVectorDB(**kwargs)

    makedirs_calls = []

    def fake_makedirs(path, exist_ok=False):
        makedirs_calls.append((path, exist_ok))

    monkeypatch.setattr(vectorstore, "FAISS", FakeFAISS)
    monkeypatch.setattr(vectorstore.os, "makedirs", fake_makedirs)
    monkeypatch.setattr(vectorstore.faiss, "IndexHNSWFlat", lambda d, n: index_criado)
    monkeypatch.setattr(vectorstore, "InMemoryDocstore", lambda _: docstore_criado)

    class FakeEmb:
        def embed_query(self, _):
            return [0.0] * 4

    monkeypatch.setattr(vectorstore, "genai_embedding", lambda: FakeEmb())

    retorno = vectorstore.build_faiss(["chunk"], url=url)

    assert retorno.saved_path == expected_path
    assert retorno.docs == ["chunk"]
    assert any(c[0] == expected_path for c in makedirs_calls)


def test_get_or_create_vectorstore_reaproveita(monkeypatch):
    monkeypatch.setattr(
        vectorstore,
        "load_vectorstore_if_exists",
        lambda **kw: "existente" if kw.get("url") else None,
    )
    monkeypatch.setattr(vectorstore, "build_faiss", lambda *a, **k: "novo")
    assert (
        vectorstore.get_or_create_vectorstore(["chunk"], url="https://a.com")
        == "existente"
    )


def test_get_or_create_vectorstore_cria_novo(monkeypatch):
    monkeypatch.setattr(vectorstore, "load_vectorstore_if_exists", lambda **kw: None)
    monkeypatch.setattr(
        vectorstore,
        "build_faiss",
        lambda chunks, url: "novo",
    )
    assert (
        vectorstore.get_or_create_vectorstore(["chunk"], url="https://b.com") == "novo"
    )
