## SQL Tutor

A local RAG (Retrieval-Augmented Generation) chatbot that answers SQL questions using a curated knowledge base, HuggingFace embeddings, ChromaDB, and a locally running Ollama LLM — served through a Gradio web interface.

---

## How it works

| File | Role |
|---|---|
| `sql-tutor/ingest.py` | Loads markdown files from `knowledge-base/`, chunks them, embeds them, and stores them in ChromaDB |
| `sql-tutor/answer.py` | Retrieves relevant chunks for a question and calls Ollama to generate an answer |
| `sql-tutor/app.py` | Launches the Gradio chat UI — imports `answer.py` directly |

---

## Prerequisites

### 1. Python 3.11+

Check your version:
```bash
python --version
```

### 2. Ollama (local LLM runtime)

Install from [ollama.com](https://ollama.com), then pull the default model:
```bash
ollama pull llama3.2
```

Make sure Ollama is running before starting the app:
```bash
ollama serve
```

### 3. Environment variables (optional)

Create a `.env` file inside `sql-tutor/` if you want to override defaults:
```
OLLAMA_MODEL=llama3.2
OLLAMA_BASE_URL=http://localhost:11434
```

---

## Install packages

From the project root, install all dependencies:

```bash
pip install -r requirements.txt
```

Or, if you use `uv` (recommended — uses `pyproject.toml`):
```bash
uv sync
```

### Key packages used by this project

| Package | Purpose |
|---|---|
| `gradio` | Web chat UI |
| `langchain`, `langchain-core`, `langchain-text-splitters` | Document loading, chunking, and RAG pipeline |
| `langchain-chroma` | ChromaDB vector store integration |
| `langchain-huggingface` | Local HuggingFace sentence embeddings |
| `langchain-ollama` | Ollama LLM integration |
| `langchain-community` | `DirectoryLoader` / `TextLoader` for markdown files |
| `chromadb` | Persistent vector database |
| `sentence-transformers` | Backing library for `all-MiniLM-L6-v2` embedding model |
| `python-dotenv` | Loads `.env` configuration |

---

## Running the project

All commands should be run from the `sql-tutor/` directory:

```bash
cd sql-tutor
```

### Step 1 — Ingest the knowledge base

Run this once, and again any time you add or change markdown files in `knowledge-base/`:

```bash
python ingest.py
```

This will:
- Load all `.md` files from `knowledge-base/` (categories: `basics`, `joins`, `ddl_dml`, `advanced`)
- Split them into overlapping chunks (size 600, overlap 150)
- Embed them using `all-MiniLM-L6-v2` (downloaded automatically on first run)
- Save the vectors to `vector_db/`

### Step 2 — Start the chat app

```bash
python app.py
```

This will open the Gradio interface in your browser. The app:
- Accepts SQL questions in a chat window
- Retrieves the 8 most relevant knowledge-base chunks
- Sends them along with your question to the local Ollama LLM
- Displays the answer and shows retrieved context in a side panel

> `answer.py` does not need to be run directly — `app.py` imports it automatically.

---

## Knowledge base structure

```
sql-tutor/knowledge-base/
├── basics/       # SELECT, WHERE, ORDER BY, etc.
├── joins/        # INNER JOIN, LEFT JOIN, etc.
├── ddl_dml/      # CREATE, INSERT, UPDATE, DELETE, etc.
└── advanced/     # Window functions, CTEs, indexes, transactions, etc.
```

Add or edit `.md` files here, then re-run `ingest.py` to update the vector store.
