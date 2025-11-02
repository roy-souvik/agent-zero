import streamlit as st
from dotenv import load_dotenv
from pages import rag_qa, chat_agent, settings
from pages import dashboard, incident_analysis, incident_reports, settings

load_dotenv()

# Page config
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title("🧭 Navigation")
# page = st.sidebar.radio(
#     "Go to",
#     ["RAG Q&A", "Chat Agent", "Settings"]
# )

navigation_links = ["RAG Q&A", "Dashboard", "Incident Analysis", "Reports", "Settings"]

page = st.sidebar.radio("Go to", navigation_links)

st.sidebar.divider()
st.sidebar.info("💡 Select a page from above to get started")

# Route to appropriate page
if page == "RAG Q&A":
    rag_qa.show()
elif page == "Dashboard":
    dashboard.show()
elif page == "Incident Analysis":
    incident_analysis.show()
elif page == "Reports":
    incident_reports.show()
elif page == "Settings":
    settings.show()