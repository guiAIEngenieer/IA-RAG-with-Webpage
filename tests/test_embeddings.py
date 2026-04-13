from app.pipeline import embeddings


def test_genai_embedding_cria_instancia(monkeypatch):
    capturado = {}

    class FakeGoogleEmbeddings:
        def __init__(self, model, google_api_key=None, **kwargs):
            capturado["model"] = model
            capturado["google_api_key"] = google_api_key

    monkeypatch.setattr(embeddings, "GoogleGenerativeAIEmbeddings", FakeGoogleEmbeddings)

    instancia = embeddings.genai_embedding()

    assert isinstance(instancia, FakeGoogleEmbeddings)
    assert capturado["model"] == "gemini-embedding-2-preview"
    assert capturado["google_api_key"] == "test-key"
