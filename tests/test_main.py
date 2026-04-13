from app import main as app_main
from langchain_core.messages import AIMessage, HumanMessage


def test_main_executa_loop_e_sai(monkeypatch):
    eventos = {"invokes": [], "logs": []}

    class FakeChain:
        def invoke(self, payload):
            eventos["invokes"].append(payload)
            return "resposta"

    monkeypatch.setattr(app_main, "get_required_settings", lambda: ("key", "https://example.com"))
    monkeypatch.setattr(app_main, "run_ingest", lambda _: "vectorstore")
    monkeypatch.setattr(app_main, "build_chain", lambda _: FakeChain())

    entradas = iter(["pergunta valida", "sair"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    monkeypatch.setattr(app_main, "validate_prompt", lambda _: None)
    monkeypatch.setattr(app_main.logger, "info", lambda msg: eventos["logs"].append(msg))

    app_main.main()

    assert eventos["invokes"] == [{"query": "pergunta valida", "chat_history": []}]
    assert eventos["logs"]


def test_main_quando_prompt_invalido_nao_invoca_chain(monkeypatch):
    chamadas = {"invokes": 0, "errors": []}

    class FakeChain:
        def invoke(self, payload):
            chamadas["invokes"] += 1
            return payload

    monkeypatch.setattr(app_main, "get_required_settings", lambda: ("key", "https://example.com"))
    monkeypatch.setattr(app_main, "run_ingest", lambda _: "vectorstore")
    monkeypatch.setattr(app_main, "build_chain", lambda _: FakeChain())

    entradas = iter(["x", "sair"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    monkeypatch.setattr(app_main, "validate_prompt", lambda _: "erro de prompt")
    monkeypatch.setattr(app_main.logger, "error", lambda msg: chamadas["errors"].append(msg))

    app_main.main()

    assert chamadas["invokes"] == 0
    assert chamadas["errors"] == ["erro de prompt"]


def test_main_persiste_historico_entre_turnos(monkeypatch):
    eventos = {"invokes": []}

    class FakeChain:
        def invoke(self, payload):
            eventos["invokes"].append(payload)
            return "resposta"

    monkeypatch.setattr(app_main, "get_required_settings", lambda: ("key", "https://example.com"))
    monkeypatch.setattr(app_main, "run_ingest", lambda _: "vectorstore")
    monkeypatch.setattr(app_main, "build_chain", lambda _: FakeChain())
    monkeypatch.setattr(app_main, "validate_prompt", lambda _: None)

    entradas = iter(["primeira pergunta", "segunda pergunta", "sair"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))
    monkeypatch.setattr(app_main.logger, "info", lambda _: None)

    app_main.main()

    assert len(eventos["invokes"]) == 2
    assert eventos["invokes"][0]["chat_history"] == []
    assert len(eventos["invokes"][1]["chat_history"]) == 2
    assert isinstance(eventos["invokes"][1]["chat_history"][0], HumanMessage)
    assert isinstance(eventos["invokes"][1]["chat_history"][1], AIMessage)


def test_main_limpa_historico(monkeypatch):
    eventos = {"invokes": [], "logs": []}

    class FakeChain:
        def invoke(self, payload):
            eventos["invokes"].append(payload)
            return "ok"

    monkeypatch.setattr(app_main, "get_required_settings", lambda: ("key", "https://example.com"))
    monkeypatch.setattr(app_main, "run_ingest", lambda _: "vectorstore")
    monkeypatch.setattr(app_main, "build_chain", lambda _: FakeChain())
    monkeypatch.setattr(app_main, "validate_prompt", lambda _: None)
    monkeypatch.setattr(app_main.logger, "info", lambda msg: eventos["logs"].append(msg))

    entradas = iter(["pergunta", "limpar", "nova pergunta", "sair"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))

    app_main.main()

    assert len(eventos["invokes"]) == 2
    assert eventos["invokes"][1]["chat_history"] == []
    assert any("cleared" in log.lower() for log in eventos["logs"])


def test_main_quando_chain_falha_continua_loop(monkeypatch):
    erros = []
    chamadas = {"invokes": 0}

    class FakeChain:
        def invoke(self, payload):
            chamadas["invokes"] += 1
            if chamadas["invokes"] == 1:
                raise RuntimeError("falha")
            return "ok"

    monkeypatch.setattr(app_main, "get_required_settings", lambda: ("key", "https://example.com"))
    monkeypatch.setattr(app_main, "run_ingest", lambda _: "vectorstore")
    monkeypatch.setattr(app_main, "build_chain", lambda _: FakeChain())
    monkeypatch.setattr(app_main, "validate_prompt", lambda _: None)
    monkeypatch.setattr(app_main.logger, "exception", lambda msg: erros.append(msg))
    monkeypatch.setattr(app_main.logger, "info", lambda _: None)

    entradas = iter(["pergunta 1", "pergunta 2", "sair"])
    monkeypatch.setattr("builtins.input", lambda _: next(entradas))

    app_main.main()

    assert chamadas["invokes"] == 2
    assert erros
