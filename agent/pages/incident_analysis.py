import streamlit as st

def show():
    st.title("🔍 Incident Analysis")

    uploaded_file = st.file_uploader("Upload incident logs (JSON)", type=['json', 'txt'])
    alert_text = st.text_area("Or paste alert message:")

    if st.button("🤖 Analyze Incident", type="primary"):
        with st.spinner("Analyzing..."):
            # Mock analysis
            st.success("✅ Analysis Complete")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Severity", "CRITICAL", "⚠️")
                st.write("**Probable Cause:** Database connection timeout")
            with col2:
                st.write("**Remediation Steps:**")
                st.markdown("1. Check DB connection pool\n2. Restart service\n3. Scale instances")

            if st.button("📋 Create Ticket"):
                st.success("Ticket #INC-2024-001 created")