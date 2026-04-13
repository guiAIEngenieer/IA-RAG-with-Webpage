import os

# Definir antes de importar módulos que leem variáveis de ambiente no import.
os.environ.setdefault("GEMINI_API_KEY", "test-key")
os.environ.setdefault("URL", "https://example.com")
