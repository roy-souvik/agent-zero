import streamlit as st
from dotenv import load_dotenv
from pages import rag_qa, chat_agent, settings, deepagent_ui

load_dotenv()

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
    ["RAG Q&A", "Chat Agent", "Deepagent", "Settings"]
)

st.sidebar.divider()
st.sidebar.info("💡 Select a page from above to get started")

# Route to appropriate page
if page == "RAG Q&A":
    rag_qa.show()
elif page == "Chat Agent":
    chat_agent.show()
elif page == "Deepagent":
    deepagent_ui.show()
elif page == "Settings":
    settings.show()