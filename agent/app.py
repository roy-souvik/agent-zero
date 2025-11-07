import streamlit as st
from dotenv import load_dotenv
from pages import (
    dashboard, incident_analysis_crew, reports_incidents,
    reports_alerts, settings
)
from utils.styles import get_custom_css

load_dotenv()

# Page config
st.set_page_config(
    page_title="Incident Management AI",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Initialize session state for user
if 'user_logged_in' not in st.session_state:
    st.session_state.user_logged_in = False
    st.session_state.username = None

# Login check
# User info in top right
col1, col2 = st.columns([6, 1])

with col2:
    st.markdown(f"""
    <div class="user-info">
        <div class="user-avatar">{st.session_state.username[0].upper() if st.session_state.username else "U"}</div>
        <div class="user-name">{st.session_state.username or "User"}</div>
    </div>
    """, unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-size: 28px;
                    font-weight: 800;
                    margin: 0;">
            🚨 IncidentAI
        </h1>
        <p style="color: rgba(255,255,255,0.5); font-size: 12px; margin: 4px 0 0 0;">
            AI-Powered Incident Management
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    page = st.radio(
        "Navigation",
        ["📊 Dashboard", "🔍 Analyze Incident", "📋 Incidents Report",
            "🔔 Alerts Report", "⚙️ Settings", "🔐 Logout"],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown("""
    <div style="background: rgba(139, 92, 246, 0.1);
                border: 1px solid rgba(139, 92, 246, 0.3);
                border-radius: 12px;
                padding: 16px;
                margin-top: 20px;">
        <p style="color: rgba(255,255,255,0.5); font-size: 11px; margin: 0 0 8px 0; text-transform: uppercase; letter-spacing: 1px;">
            Powered By
        </p>
        <p style="color: white; font-size: 13px; margin: 4px 0; font-weight: 500;">
            🤖 LangGraph Multi-Agents
        </p>
        <p style="color: white; font-size: 13px; margin: 4px 0; font-weight: 500;">
            🔗 MCP Servers
        </p>
        <p style="color: white; font-size: 13px; margin: 4px 0; font-weight: 500;">
            🧠 Ollama LLM
        </p>
    </div>
    """, unsafe_allow_html=True)

# Route to pages
if page == "🔐 Logout":
    st.session_state.user_logged_in = False
    st.session_state.username = None
    st.rerun()
elif page == "📊 Dashboard":
    dashboard.show()
elif page == "🔍 Analyze Incident":
    incident_analysis_crew.show()
elif page == "📋 Incidents Report":
    reports_incidents.show()
elif page == "🔔 Alerts Report":
    reports_alerts.show()
elif page == "⚙️ Settings":
    settings.show()