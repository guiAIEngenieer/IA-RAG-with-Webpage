import pytest

from app.pipeline import loaders


def test_loader_web_retorna_dados(monkeypatch):
    esperado = ["conteudo"]

    class FakeLoader:
        def __init__(self, url=None, max_depth=None, continue_on_failure=None, **kwargs):
            self.url = url

        def load(self):
            assert self.url == "https://example.com"
            return esperado

    monkeypatch.setattr(loaders, "RecursiveUrlLoader", FakeLoader)

    assert loaders.loader_web("https://example.com") == esperado


def test_loader_web_relanca_excecao(monkeypatch):
    class FakeLoader:
        def __init__(self, **kwargs):
            pass

        def load(self):
            raise RuntimeError("erro loader")

    monkeypatch.setattr(loaders, "RecursiveUrlLoader", FakeLoader)

    with pytest.raises(RuntimeError):
        loaders.loader_web("https://example.com")
