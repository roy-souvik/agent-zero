import streamlit as st

def show():
    st.title("🔥 Incident Dashboard")

    col1, col2, col3 = st.columns(3)
    col1.metric("Active Incidents", "3", "-1")
    col2.metric("Critical Alerts", "12", "+5")
    col3.metric("Avg Resolution Time", "2.5h", "-0.3h")

    st.subheader("Recent Incidents")
    # Mock data table
    st.dataframe({"ID": [1,2,3], "Severity": ["High","Medium","Critical"], "Status": ["Open","Resolved","Open"]})