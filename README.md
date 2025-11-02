# AI Infra

### LangChain + Ollama + Chroma + Streamlit + FastAPI

A modular AI Agent environment combining **LangChain**, **Ollama**, **ChromaDB**, **Streamlit**, and **FastAPI** — all running in Docker.

---

## 🏗️ Features
- **Ollama**: Local LLM backend (Llama3, Mistral, etc.)
- **ChromaDB**: Vector database for RAG and memory
- **LangChain Agent**: Manages tools, reasoning, and embeddings
- **Crew AI Framework**: Manages AI agents
- **Streamlit**: Interactive UI
- **FastAPI**: REST interface for backend communication
- **Dockerized**: Fully isolated and reproducible environment

---

## 🚀 Setup

### 1️⃣ Clone & Configure
```bash
git clone https://github.com/roy-souvik/agent-zero.git
cd agent-zero
cp .env.example .env
