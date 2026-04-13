import importlib
import sys
import types


def test_get_chat_model_config(monkeypatch):
    google_mod = types.ModuleType("langchain_google_genai")

    class FakeChatGoogleGenerativeAI:
        def __init__(self, model, api_key, temperature):
            self.model = model
            self.api_key = api_key
            self.temperature = temperature

    google_mod.ChatGoogleGenerativeAI = FakeChatGoogleGenerativeAI
    monkeypatch.setitem(sys.modules, "langchain_google_genai", google_mod)

    if "app.rag.llms" in sys.modules:
        del sys.modules["app.rag.llms"]

    llms = importlib.import_module("app.rag.llms")

    m = llms.get_chat_model()
    assert m.model == llms.MODEL_GENAI
    assert m.temperature == llms.TEMP_GENAI
    assert m.api_key == "test-key"
