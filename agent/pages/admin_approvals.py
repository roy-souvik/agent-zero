import streamlit as st
import pandas as pd
from datetime import datetime
import random

@st.cache_data
def get_pending_data():
    data = []
    for i in range(15):
        data.append({
            "ID": i + 1,
            "Payload_ID": f"PLD-{1000 + i}",
            "Environment": random.choice(["production", "staging", "dev"]),
            "Severity": random.choice(["Critical", "High", "Medium", "Low"]),
            "Model_Score": round(random.uniform(0.65, 0.95), 2),
            "Rule_Score": round(random.uniform(0.60, 0.90), 2),
            "Combined_Score": round(random.uniform(0.62, 0.92), 2),
            "Source": random.choice(["API", "Database", "Network"]),
            "Corrective_Action": random.choice(["Restart service", "Scale resources", "Check connections"])
        })
    return pd.DataFrame(data)

@st.dialog("Approve Record")
def approval_dialog(record):
    st.write(f"**Payload ID:** {record['Payload_ID']}")
    st.write(f"**Environment:** {record['Environment']}")
    st.write(f"**Current Severity:** {record['Severity']}")
    st.write(f"**Combined Score:** {record['Combined_Score']}")
    st.write(f"**Corrective Action:** {record['Corrective_Action']}")

    st.divider()

    final_severity = st.selectbox(
        "Final Severity",
        ["Critical", "High", "Medium", "Low"],
        index=["Critical", "High", "Medium", "Low"].index(record['Severity'])
    )

    notes = st.text_area("Approver Notes", height=100)

    if st.button("Approve", type="primary"):
        st.session_state.approved_ids.append(record['ID'])
        st.session_state.approval_data.append({
            'Payload_ID': record['Payload_ID'],
            'Original_Severity': record['Severity'],
            'Approved_Severity': final_severity,
            'Notes': notes,
            'Approved_By': st.session_state.get('username', 'admin'),
            'Approved_At': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.success("Approved successfully")
        st.rerun()

def show():
    st.title("Admin Approvals")

    if 'approved_ids' not in st.session_state:
        st.session_state.approved_ids = []
    if 'approval_data' not in st.session_state:
        st.session_state.approval_data = []

    tab1, tab2 = st.tabs(["Pending", "Approved"])

    with tab1:
        df = get_pending_data()
        df = df[~df['ID'].isin(st.session_state.approved_ids)]

        col1, col2, col3 = st.columns(3)
        col1.metric("Pending", len(df))
        col2.metric("Critical", len(df[df['Severity']=='Critical']))
        col3.metric("Avg Score", f"{df['Combined_Score'].mean():.2f}")

        col1, col2, col3 = st.columns(3)
        env = col1.selectbox("Environment", ["All"] + df['Environment'].unique().tolist())
        sev = col2.selectbox("Severity", ["All"] + df['Severity'].unique().tolist())
        src = col3.selectbox("Source", ["All"] + df['Source'].unique().tolist())

        if env != "All":
            df = df[df['Environment'] == env]
        if sev != "All":
            df = df[df['Severity'] == sev]
        if src != "All":
            df = df[df['Source'] == src]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Model_Score": st.column_config.NumberColumn(format="%.2f"),
                "Rule_Score": st.column_config.NumberColumn(format="%.2f"),
                "Combined_Score": st.column_config.NumberColumn(format="%.2f")
            }
        )

        record_id = st.number_input("Enter ID to approve", min_value=1, max_value=15, step=1)

        if st.button("Approve", type="primary"):
            record = df[df['ID'] == record_id]
            if not record.empty:
                approval_dialog(record.iloc[0])
            else:
                st.error("Record not found in pending list")

    with tab2:
        if st.session_state.approval_data:
            approved_df = pd.DataFrame(st.session_state.approval_data)
            st.dataframe(approved_df, use_container_width=True, hide_index=True)

            csv = approved_df.to_csv(index=False).encode('utf-8')
            st.download_button("Export CSV", csv, "approved.csv", "text/csv")
        else:
            st.info("No approved records")