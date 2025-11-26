import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_chroma import Chroma
import chromadb
from collections import defaultdict
import threading
from tracer import InMemoryTracer

# Load environment variables
load_dotenv()

# Config
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))

# ==================== In-Memory Tracing System ====================

# Global tracer instance
tracer = InMemoryTracer()


def trace_operation(operation_name: str):
    """Decorator to automatically trace function calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            start = time.time()

            # Prepare input data (limit size for memory)
            input_data = {
                "args": str(args)[:200],
                "kwargs": str(kwargs)[:200]
            }

            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start) * 1000

                # Prepare output data
                output_data = {
                    "result": str(result)[:500] if result else None
                }

                tracer.add_trace(
                    operation=operation_name,
                    input_data=input_data,
                    output_data=output_data,
                    duration_ms=duration_ms,
                    status="success"
                )

                return result

            except Exception as e:
                duration_ms = (time.time() - start) * 1000
                tracer.add_trace(
                    operation=operation_name,
                    input_data=input_data,
                    output_data={},
                    duration_ms=duration_ms,
                    status="error",
                    error=str(e)
                )
                raise

        return wrapper
    return decorator


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

    return response.content


@trace_operation("semantic_search")
def semantic_search(query: str, k: int = 3):
    """Search documents semantically with tracing."""
    db = init_vector_store()
    results = db.similarity_search(query, k=k)
    return results


# ==================== Observability Endpoints ====================

def get_traces_api(operation: str = None, limit: int = 100):
    """Get traces for API endpoint"""
    return tracer.get_traces(operation=operation, limit=limit)


def get_stats_api():
    """Get statistics for API endpoint"""
    return tracer.get_stats()


def export_traces_api(filepath: str = "traces.json"):
    """Export traces to JSON file"""
    tracer.export_json(filepath)
    return {"status": "Traces exported to " + filepath}