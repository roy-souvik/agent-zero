import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
import chromadb
from guardrails import Guard
from guardrails.hub import hallucination_check, security_incident_policy

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

# Initialize Guardrails (auto-validates LLM outputs)
guard = Guard.from_string(
    validators=[
        hallucination_check(),          # prevents unsupported or made-up fixes
        security_incident_policy()      # blocks unsafe or policy-violating responses
    ],
    description="Ensure the solution is accurate, safe, and policy-compliant."
)

def init_vector_store():
    """Initialize Chroma client and collection."""
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
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
    """Query Chroma, use context for generation, and validate with Guardrails."""
    db = init_vector_store()
    docs = db.similarity_search(question, k=3)

    if not docs:
        return "No similar documents found."

    context = "\n".join([d.page_content for d in docs])
    prompt = f"""You are a helpful AI assistant.
Use the context below to answer accurately and concisely.

Context:
{context}

Question: {question}
Answer:"""

    raw_response = llm.invoke(prompt).content
    validated_response = guard.parse(raw_response)  # Guardrails validation
    return validated_response
