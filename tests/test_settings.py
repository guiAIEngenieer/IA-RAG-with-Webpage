import importlib
import os
import sys

import pytest


def test_get_required_settings_lanca_erro_sem_variaveis(monkeypatch):
    monkeypatch.setattr(os, "getenv", lambda _: None)

    if "app.settings" in sys.modules:
        del sys.modules["app.settings"]

    settings = importlib.import_module("app.settings")

    with pytest.raises(ValueError):
        settings.get_required_settings()


def test_get_required_settings_carrega_variaveis(monkeypatch):
    valores = {"GEMINI_API_KEY": "abc", "URL": "https://example.com"}
    monkeypatch.setattr(os, "getenv", lambda chave: valores.get(chave))

    if "app.settings" in sys.modules:
        del sys.modules["app.settings"]

    settings = importlib.import_module("app.settings")
    key, url = settings.get_required_settings()
    assert key == "abc"
    assert url == "https://example.com"
