import streamlit as st

def show():
    st.title("📊 Incident Reports")

    # Filters
    col1, col2 = st.columns(2)
    severity = col1.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])
    date_range = col2.date_input("Date Range")

    # Mock reports list
    st.dataframe({
        "ID": ["INC-001", "INC-002"],
        "Date": ["2024-11-01", "2024-10-28"],
        "Severity": ["Critical", "High"],
        "Summary": ["DB timeout", "High CPU"]
    })

    if st.button("📥 Export Report"):
        st.download_button("Download", data="mock_report.pdf", file_name="incident_report.pdf")