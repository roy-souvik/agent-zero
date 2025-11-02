import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
import chromadb

# Load environment variables
load_dotenv()

# Config
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))
CHROMA_DIR = os.getenv("CHROMA_DIR", "/chroma")

# Initialize embeddings and LLM
embeddings = OllamaEmbeddings(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_URL)

def init_vector_store():
    client = chromadb.HttpClient(
        host=CHROMA_HOST,
        port=CHROMA_PORT
    )

    return Chroma(
        collection_name="docs",
        embedding_function=embeddings,
        client=client,
    )

def add_document(text: str):
    """Add text/document to Chroma DB."""
    db = init_vector_store()
    db.add_texts([text])
    return {"status": "Document added successfully"}


def query_rag(question: str):
    """Query Chroma and use context for generation."""
    db = init_vector_store()
    docs = db.similarity_search(question, k=3)

    if not docs:
        return "No similar documents found."

    context = "\n".join([d.page_content for d in docs])
    prompt = f"""You are a helpful AI assistant.
Use the context below to answer the question accurately.

Context:
{context}

Question: {question}
Answer:"""

    response = llm.invoke(prompt)
    return response.content
