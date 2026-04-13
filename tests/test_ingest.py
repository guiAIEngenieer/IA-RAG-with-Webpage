import pytest

from app.pipeline import ingest


def test_run_ingest_fluxo_feliz(monkeypatch):
    monkeypatch.setattr(ingest, "load_vectorstore_if_exists", lambda **kw: None)
    monkeypatch.setattr(ingest, "loader_web", lambda url: ["pagina", url])
    monkeypatch.setattr(ingest, "chunking", lambda page: ["chunk", page[1]])
    monkeypatch.setattr(
        ingest,
        "get_or_create_vectorstore",
        lambda chunks, url: {"chunks": chunks, "url": url},
    )

    retorno = ingest.run_ingest("https://example.com")

    assert retorno == {"chunks": ["chunk", "https://example.com"], "url": "https://example.com"}


def test_run_ingest_relanca_excecao(monkeypatch):
    monkeypatch.setattr(
        ingest,
        "loader_web",
        lambda _: (_ for _ in ()).throw(RuntimeError("erro")),
    )

    with pytest.raises(RuntimeError):
        ingest.run_ingest("https://example.com")
