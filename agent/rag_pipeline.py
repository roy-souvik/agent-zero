import os
import json
import tiktoken
from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
import chromadb
from tracing import trace_operation
from tracer_instance import tracer

# Load environment variables
load_dotenv()

# Config
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))

# ==================== RAG Pipeline ====================

# Initialize embeddings and LLM
embeddings = OllamaEmbeddings(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_URL, temperature=0.7)


def init_vector_store():
    """Initialize Chroma vector store."""
    client = chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT
    )
    return Chroma(
        collection_name="docs",
        embedding_function=embeddings,
        client=client,
    )


@trace_operation("add_document")
def add_document(text: str):
    """Add text/document to Chroma DB with tracing."""
    db = init_vector_store()
    db.add_texts([text])
    return {"status": "Document added successfully"}


@trace_operation("query_rag")
def query_rag(question: str):
    """Query Chroma and use context for generation with tracing."""
    # Retrieve documents
    db = init_vector_store()
    docs = db.similarity_search(question, k=3)

    if not docs:
        return "No similar documents found."

    # Prepare context
    context = "\n".join([d.page_content for d in docs])
    prompt = f"""You are a helpful AI assistant.
Use the context below to answer the question accurately.

Context:
{context}

Question: {question}
Answer:"""

    # Generate response
    response = llm.invoke(prompt.strip())

    encoding_token = tiktoken.get_encoding("cl100k_base")
    input_tokens = len(encoding_token.encode(prompt))
    output_tokens = len(encoding_token.encode(response.content))

    # Store in tracer
    tracer.add_trace(
        operation="query_rag_tokens",
        input_data={"input_tokens": input_tokens},
        output_data={"output_tokens": output_tokens, "total_tokens": input_tokens + output_tokens},
        duration_ms=0,
        status="success"
    )

    return response.content


@trace_operation("semantic_search")
def semantic_search(query: str, k: int = 3):
    """Search documents semantically with tracing."""
    db = init_vector_store()
    results = db.similarity_search(query, k=k)
    return results
