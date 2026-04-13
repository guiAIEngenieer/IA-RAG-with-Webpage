# Area de testes

Esta pasta centraliza os testes automatizados do projeto.

## Como executar

1. Instale as dependencias:
   - `pip install -r requirements.txt`
2. Rode os testes:
   - `pytest -q`

## Cobertura atual

- `pipeline`: loaders, chunker, embeddings, vectorstore, ingest
- `rag`: retriever, chains, llms
- `utils`: validations, evaluation
- fluxo principal: `app.main`
- configuracao: `app.settings`
