# IA RAG with Webpage | RAG sobre páginas web (CLI)

O sistema indexa o conteúdo de uma Pagina Web completa , através de uma **URL** configurável, recupera trechos relevantes a cada pergunta e gera respostas contextualizadas, com **memória** para manter o diálogo coerente.

---

## Visão geral

**IA RAG with Webpage** explora na prática um pipeline clássico de RAG: **carregar documentos da web**, **fragmentar (chunking)**, **vetorizar com embeddings Gemini**, **armazenar em FAISS** e **consultar um modelo de linguagem** com contexto recuperado e histórico de chat além da inclusão de técnicas avançadas como **Rewrite Retrieval** , **Rerank** e **QA Generation**. Tudo isso acessível por uma **interface de linha de comando** simples.

---

## Funcionalidades principais

- **Ingestão a partir de URL** : carrega páginas (com fallback quando o carregamento recursivo estoura tempo).
- **Índice vetorial por fonte** : cada URL normalizada possui seu próprio diretório sob `faiss-db/`, evitando misturar bases de conhecimento.
- **Recuperação top-k** : o retriever busca os trechos mais próximos da pergunta atual.
- **Chat com histórico** : as últimas interações entram no prompt (com limite de turnos configurável).
- **Comandos no terminal** : `ajuda`, `url`, `limpar`, `sair`, além de validação de tamanho do prompt.
- **Logging estruturado** : saída em console e arquivo rotacionado em `logs/`.

---

## Como o sistema funciona

### Fluxo de RAG (por pergunta)

1. **Pergunta do usuário** entra na chain junto com o **histórico de mensagens** já truncado.
2. O **retriever** usa a pergunta para buscar documentos similares no **FAISS** (embeddings Gemini).
3. Os trechos recuperados são **concatenados** como contexto textual.
4. O **prompt** (LangChain) combina instruções de sistema, histórico e bloco `Context: … / Question: …`.
5. O **Gemini** (`gemini-2.5-flash`) gera a resposta, que é exibida no terminal e anexada ao histórico.

Não há roteamento entre múltiplos “agentes” nem grafo de estados: o fluxo é **linear** (recuperação → geração).

### Memória da conversa

- O histórico é uma lista de mensagens **LangChain** (`HumanMessage` / `AIMessage`).
- A função `truncate_history` limita o número de turnos (`MAX_CHAT_TURNS` em `app/config/constants.py`), evitando prompts excessivamente longos.
- O comando **`limpar`** zera o histórico **na sessão atual** sem reiniciar o índice FAISS.

### Primeira execução e índice

Na subida do programa, `run_ingest` verifica se já existe índice para a `URL` do `.env`. Se existir, **reutiliza**; caso contrário, executa carga da web, chunking e construção do FAISS.

---

## Tecnologias

| Camada | Tecnologia |
|--------|------------|
| Linguagem | Python 3.10+ (recomendado) |
| Orquestração LLM | [LangChain](https://www.langchain.com/) |
| Modelo de chat | Google Gemini (`gemini-2.5-flash`) |
| Embeddings | Google Generative AI (`gemini-embedding-2-preview`) |
| Vetores | [FAISS](https://github.com/facebookresearch/faiss) (`faiss-cpu`) |
| Carga web | `langchain_community` (RecursiveUrlLoader / WebBaseLoader) |
| Configuração | `python-dotenv` |
| Testes | `pytest` |

Dependências adicionais (p.ex. avaliação com chains clássicas) estão listadas em `requirements.txt`.

---

## Pré-requisitos

- [Python](https://www.python.org/) **3.10 ou superior**
- Conta Google e **API key** do Gemini ([Google AI Studio](https://aistudio.google.com/))
- URL **http/https** válida para indexar

---

## Instalação e execução

### 1. Clonar o repositório

```bash
git clone https://github.com/SEU_USUARIO/SEU_REPO.git
cd SEU_REPO
```

### 2. Ambiente virtual

```bash
python -m venv .venv

# Windows
.\.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Dependências

```bash
pip install -r requirements.txt
```

### 4. Variáveis de ambiente

Na raiz do projeto, crie um arquivo **`.env`** (você pode usar o arquivo de exemplo `.env.exemple` como referência):

```env
GEMINI_API_KEY=sua_chave_aqui
URL=https://exemplo.com
```

- **`GEMINI_API_KEY`** : chave do Google AI Studio.  
- **`URL`** : site (ou página inicial) cujo conteúdo será indexado para o RAG.

Sem essas variáveis, `get_required_settings()` encerra com erro explícito.

### 5. Executar o chat

Na raiz do projeto:

```bash
python -m app
```

ou:

```bash
python -m app.main
```

Na primeira vez, o ingest pode demorar enquanto a página é baixada e o índice é criado. Execuções seguintes reutilizam o FAISS em disco quando a URL é a mesma.

---

## Uso no terminal

Após o banner, o prompt aparece como:

```text
rag>
```

| Entrada | Efeito |
|--------|--------|
| Texto livre | Pergunta ao RAG (após validação de tamanho). |
| `ajuda` | Lista os comandos. |
| `url` | Mostra a URL de fonte carregada do `.env`. |
| `limpar` | Apaga o histórico da conversa atual. |
| `sair` | Encerra o programa. |

**Exemplos de perguntas** (ajuste ao tema do site indexado):

- `Quais são os principais tópicos abordados na página inicial?`
- `Resuma o conteúdo sobre [tema específico] em três bullet points.`
- `Há menção a prazos ou datas importantes?`

**Dica:** para trocar a fonte de conhecimento, altere `URL` no `.env`, apague ou isole o subdiretório correspondente em `faiss-db/` se quiser forçar reindexação, e execute novamente.

---

## Estrutura do projeto (resumo)

```text
app/
  main.py              # Loop CLI
  settings.py          # GEMINI_API_KEY e URL
  config/constants.py  # Modelos, chunking, FAISS, limites de histórico
  pipeline/            # loaders, chunker, ingest, embeddings, vectorstore
  rag/                 # prompts, retriever, LLM, chain RAG
  utils/               # validação, histórico, utilitários
  core/logger.py       # Logging com rotação
logs/                  # Gerado em runtime (gitignored)
faiss-db/              # Índices por URL (gitignored)
tests/                 # Testes com pytest
```

---

## Testes

```bash
pytest
```

---

## Agradecimentos

Fala, pessoal!

É com muita satisfação que compartilho mais um projeto que desenvolvi. Desta vez, coloquei em prática diversas técnicas mais avançadas que venho aprendendo ao longo da minha jornada rumo à engenharia de IA, especialmente com os cursos da Alura.

Esse projeto foi bastante desafiador e exigiu tempo, dedicação e muito estudo, mas todo o processo valeu a pena. Foi uma experiência incrível, que me proporcionou um grande crescimento técnico e consolidou vários conhecimentos importantes. Mais do que o resultado final, essa foi uma jornada de aprendizado intensa, cheia de descobertas e evolução.

Fica aqui o convite para vocês conhecerem o projeto, explorarem e testarem da sua própria maneira. Vou ficar muito feliz em receber feedbacks e trocar ideias com vocês!

Vamos juntos evoluir cada vez mais.