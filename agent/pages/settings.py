import streamlit as st
import os

def show():
    st.title("⚙️ Settings")
    st.markdown("Configure your AI assistant")

    st.subheader("🔧 Current Configuration")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**API Settings**")
        st.info(f"API URL: `{os.getenv('API_URL', 'Not set')}`")
        st.info(f"Ollama URL: `{os.getenv('OLLAMA_URL', 'Not set')}`")
        st.info(f"Model: `{os.getenv('OLLAMA_MODEL', 'Not set')}`")

    with col2:
        st.markdown("**ChromaDB Settings**")
        st.info(f"Host: `{os.getenv('CHROMA_HOST', 'Not set')}`")
        st.info(f"Port: `{os.getenv('CHROMA_PORT', 'Not set')}`")
        st.info(f"Collection: `{os.getenv('CHROMA_COLLECTION', 'Not set')}`")

    st.divider()

    st.markdown("**⚠️ Note:** Settings are configured via environment variables")
    st.markdown("Edit your `.env` file to modify these settings")