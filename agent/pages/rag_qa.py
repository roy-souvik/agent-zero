import os
import re
import streamlit as st
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_chroma import Chroma
import chromadb
from typing import Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Config
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
CHROMA_HOST = os.getenv("CHROMA_HOST", "chroma")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", 8000))

# ==================== GUARDRAILS CLASS ====================
class LLMGuardrails:
    """Basic guardrails for local LLM applications"""

    def __init__(self):
        # Define harmful patterns
        self.harmful_patterns = [
            r'(?i)(password|secret|api.?key|token)',
            r'(?i)(execute|eval|exec|system)',
            r'(?i)(drop\s+table|delete\s+from|insert\s+into)',
        ]

        # Define content filters
        self.blocked_keywords = [
            'violence', 'harassment', 'illegal', 'exploit'
        ]

        self.max_input_length = 5000
        self.max_output_length = 2000

    def validate_input(self, user_input: str) -> tuple[bool, Optional[str]]:
        """Validate user input for safety and appropriateness"""

        # Check input length
        if len(user_input) > self.max_input_length:
            return False, f"Input exceeds maximum length of {self.max_input_length}"

        # Check for empty input
        if not user_input.strip():
            return False, "Input cannot be empty"

        # Check for harmful patterns
        for pattern in self.harmful_patterns:
            if re.search(pattern, user_input):
                return False, "Input contains potentially harmful content"

        # Check for blocked keywords
        input_lower = user_input.lower()
        for keyword in self.blocked_keywords:
            if keyword in input_lower:
                return False, f"Input contains blocked keyword: {keyword}"

        return True, None

    def filter_output(self, output: str) -> str:
        """Post-process LLM output for safety"""

        # Truncate if too long
        if len(output) > self.max_output_length:
            output = output[:self.max_output_length] + "..."

        # Remove any accidental sensitive patterns from response
        output = re.sub(r'(password|api.?key|secret)\s*[:=]\s*[^\s]+',
                       '[REDACTED]', output, flags=re.IGNORECASE)

        # Basic profanity filter (expandable)
        bad_words = ['badword1', 'badword2']
        for word in bad_words:
            output = re.sub(rf'\b{word}\b', '[FILTERED]', output, flags=re.IGNORECASE)

        return output

    def check_output_safety(self, output: str) -> tuple[bool, Optional[str]]:
        """Verify output safety before returning to user"""

        if not output.strip():
            return False, "Model generated empty output"

        # Check for repeated patterns that might indicate loops or errors
        if len(set(output.split())) < len(output.split()) * 0.1:
            return False, "Output contains excessive repetition"

        # Check for harmful keywords in output
        output_lower = output.lower()
        for keyword in self.blocked_keywords:
            if keyword in output_lower:
                return False, f"Output contains blocked keyword: {keyword}"

        return True, None

    def process_request(self, user_input: str, llm_output: str) -> dict:
        """Complete pipeline: validate input, generate output, filter result"""

        # Step 1: Validate input
        is_valid, error = self.validate_input(user_input)
        if not is_valid:
            return {
                'success': False,
                'error': error,
                'output': None
            }

        # Step 2: Check output safety
        is_safe, error = self.check_output_safety(llm_output)
        if not is_safe:
            return {
                'success': False,
                'error': error,
                'output': None
            }

        # Step 3: Filter output
        filtered_output = self.filter_output(llm_output)

        return {
            'success': True,
            'error': None,
            'output': filtered_output
        }

# ==================== INITIALIZATION ====================

# Initialize guardrails
guardrails = LLMGuardrails()

# Initialize embeddings and LLM
embeddings = OllamaEmbeddings(model=OLLAMA_MODEL, base_url=OLLAMA_URL)
llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_URL, temperature=0.3)

@st.cache_resource
def get_vector_store():
    """Initialize and cache Chroma client and collection."""
    client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return Chroma(
        collection_name="docs",
        embedding_function=embeddings,
        client=client,
    )

# ==================== FUNCTIONS ====================

def add_document(text: str) -> dict:
    """Add text/document to Chroma DB with guardrails validation."""

    # Validate input with guardrails
    is_valid, error = guardrails.validate_input(text)
    if not is_valid:
        return {
            "status": "failed",
            "message": f"❌ {error}"
        }

    try:
        db = get_vector_store()
        db.add_texts([text])
        logger.info("Document added successfully")
        return {
            "status": "success",
            "message": "✅ Document added successfully"
        }
    except Exception as e:
        logger.error(f"Error adding document: {e}")
        return {
            "status": "failed",
            "message": f"❌ Error adding document: {str(e)}"
        }

def query_rag(question: str) -> dict:
    """
    Query Chroma, use context for generation, and validate with Guardrails.

    Returns:
        dict with keys: success (bool), response (str), error (str or None)
    """

    # Step 1: Validate user input with guardrails
    is_valid, error = guardrails.validate_input(question)
    if not is_valid:
        logger.warning(f"Input validation failed: {error}")
        return {
            "success": False,
            "response": None,
            "error": f"Input validation failed: {error}"
        }

    try:
        # Step 2: Retrieve relevant documents (optional)
        db = get_vector_store()
        docs = db.similarity_search(question, k=3)

        # Step 3: Build context based on what's available
        if docs:
            context = "\n".join([d.page_content for d in docs])
            prompt = f"""You are a helpful AI assistant.
Use the context below to answer accurately and concisely.

Context:
{context}

Question: {question}
Answer:"""
            logger.info(f"Found {len(docs)} documents for: {question}")
        else:
            prompt = f"""You are a helpful AI assistant.
Answer the following question to the best of your knowledge:

Question: {question}
Answer:"""
            logger.info(f"No documents found for: {question}. Using general knowledge.")

        # Step 4: Generate response with LLM
        logger.info(f"Generating response for: {question}")
        raw_response = llm.invoke(prompt).content

        # Step 5: Validate output with guardrails
        is_safe, safety_error = guardrails.check_output_safety(raw_response)
        if not is_safe:
            logger.warning(f"Output validation failed: {safety_error}")
            return {
                "success": False,
                "response": None,
                "error": f"Response validation failed: {safety_error}"
            }

        # Step 6: Filter output for safety
        filtered_response = guardrails.filter_output(raw_response)

        logger.info("Response validated and filtered successfully")
        return {
            "success": True,
            "response": filtered_response,
            "error": None
        }

    except Exception as e:
        logger.error(f"Error in query_rag: {e}")
        return {
            "success": False,
            "response": None,
            "error": f"Error processing query: {str(e)}"
        }
# ==================== STREAMLIT UI ====================

def show():

    st.title("🔒 RAG Chatbot with Guardrails")

    # Sidebar for document upload
    with st.sidebar:
        st.header("📚 Document Management")
        st.markdown("Add documents to your knowledge base")

        doc_input = st.text_area(
            "Enter document text:",
            height=150,
            placeholder="Paste your document here..."
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Add Document", use_container_width=True):
                with st.spinner("Adding document..."):
                    result = add_document(doc_input)
                    if result["status"] == "success":
                        st.success(result["message"])
                        st.rerun()
                    else:
                        st.error(result["message"])

        with col2:
            if st.button("🗑️ Clear", use_container_width=True):
                st.rerun()

        st.divider()

        # Display connection status
        st.subheader("🔌 Connection Status")
        status_col1, status_col2 = st.columns(2)
        with status_col1:
            st.metric("Model", OLLAMA_MODEL.split(":")[0])
        with status_col2:
            st.metric("Chroma", f"{CHROMA_HOST}:{CHROMA_PORT}")

    # Main chat interface
    st.header("💬 Ask Questions About Your Documents")

    # Display guardrails info
    with st.expander("ℹ️ Guardrails Protection"):
        st.markdown("""
        **Input Guardrails:**
        - ✓ Length validation (max 5000 chars)
        - ✓ Blocked keywords detection
        - ✓ Harmful pattern detection

        **Output Guardrails:**
        - ✓ Safety checks on responses
        - ✓ Sensitive data redaction (API keys, passwords)
        - ✓ Repetition detection
        - ✓ Profanity filtering

        **Blocked Keywords:** violence, harassment, illegal, exploit
        """)

    # Chat interface
    question = st.text_input(
        "Your question:",
        placeholder="Ask something about your documents...",
        help="Type your question and press Enter"
    )

    if question:
        with st.spinner("🔄 Processing with guardrails..."):
            result = query_rag(question)

            st.divider()

            if result["success"]:
                st.success("✅ Response validated by Guardrails")
                st.markdown("### Answer")
                st.write(result["response"])
            else:
                if result["error"]:
                    st.error(f"❌ {result['error']}")
                else:
                    st.info(result["response"])

    # Footer
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.caption(f"🤖 LLM: {OLLAMA_MODEL}")
    with col2:
        st.caption(f"🗄️ Vector DB: Chroma")
    with col3:
        st.caption("🛡️ Guardrails: Active")
