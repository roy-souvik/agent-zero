import streamlit as st
from dotenv import load_dotenv
import requests

load_dotenv()

API_URL = "http://localhost:8001"

# Page config
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
page = st.sidebar.radio(
    "Go to",
    ["RAG Q&A", "Chat Agent", "Settings"]
)

st.sidebar.divider()
st.sidebar.info("💡 Select a page from above to get started")

# RAG Q&A Page
if page == "RAG Q&A":
    st.title("📚 RAG Question & Answer")
    st.markdown("Ask questions based on your document knowledge base")

    # Two column layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("💬 Ask a Question")
        question = st.text_input("Enter your question:", placeholder="What would you like to know?")

        if st.button("🔍 Ask", type="primary", use_container_width=True):
            if question.strip():
                with st.spinner("🤔 Thinking..."):
                    try:
                        res = requests.post(
                            f"{API_URL}/query",
                            json={"question": question},
                            timeout=30
                        )
                        if res.status_code == 200:
                            answer = res.json().get("answer", "No answer returned")
                            st.success("✅ Answer:")
                            st.markdown(f"**{answer}**")
                        else:
                            st.error(f"❌ Error: {res.status_code} - {res.text}")
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Request timed out. Please try again.")
                    except requests.exceptions.ConnectionError:
                        st.error("🔌 Cannot connect to API. Is the server running?")
                    except Exception as e:
                        st.error(f"❌ An error occurred: {str(e)}")
            else:
                st.warning("⚠️ Please enter a question")

    with col2:
        st.subheader("📄 Add Document")
        with st.expander("➕ Add to Knowledge Base", expanded=False):
            text = st.text_area(
                "Document text",
                placeholder="Paste your document content here...",
                height=200
            )

            if st.button("💾 Add Document", use_container_width=True):
                if text.strip():
                    with st.spinner("📤 Adding document..."):
                        try:
                            response = requests.post(
                                f"{API_URL}/add",
                                json={"text": text},
                                timeout=30
                            )
                            if response.status_code == 200:
                                st.success("✅ Document added successfully!")
                                st.balloons()
                            else:
                                st.error(f"❌ Failed to add document: {response.status_code}")
                        except requests.exceptions.Timeout:
                            st.error("⏱️ Request timed out. Please try again.")
                        except requests.exceptions.ConnectionError:
                            st.error("🔌 Cannot connect to API. Is the server running?")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
                else:
                    st.warning("⚠️ Please enter some text")

# Chat Agent Page
elif page == "Chat Agent":
    st.title("💬 Chat Agent")
    st.markdown("*Coming soon...*")
    st.info("This will be a conversational AI agent")

# Settings Page
elif page == "Settings":
    st.title("⚙️ Settings")
    st.markdown("*Coming soon...*")
    st.info("Configure your AI assistant settings here")