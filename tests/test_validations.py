import pytest

from app.utils.validations import validate_prompt, validate_source_url


def test_validate_prompt_quando_vazio():
    assert validate_prompt("") == "Invalid prompt."


def test_validate_prompt_quando_curto():
    assert validate_prompt("oi") == "Prompt too short."


def test_validate_prompt_quando_longo():
    texto = "a" * 501
    assert validate_prompt(texto) == "Prompt too long."


def test_validate_prompt_quando_valido():
    assert validate_prompt("Qual o resumo da página?") is None


def test_validate_source_url_ok():
    assert validate_source_url("https://example.com/path") == "https://example.com/path"


def test_validate_source_url_remove_trailing_slash():
    assert validate_source_url("https://ex.com/") == "https://ex.com"


def test_validate_source_url_vazia():
    with pytest.raises(ValueError):
        validate_source_url("")


def test_validate_source_url_esquema_invalido():
    with pytest.raises(ValueError):
        validate_source_url("ftp://x.com")
