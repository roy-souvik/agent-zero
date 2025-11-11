import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from database.db.connection import get_connection
from database.models.classifier_output import ClassifierOutputsModel

def get_pending_data():
    conn = get_connection()
    classifier_output = ClassifierOutputsModel(conn)
    data = classifier_output.find_unprocessed()
    # df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_approved_data():
    conn = get_connection()
    query = """
        SELECT payload_id, severity_id AS Original_Severity,
               approved_severity AS Approved_Severity,
               approved_by AS Approved_By,
               approved_ts AS Approved_At,
               approved_corrective_action AS Approved_Action
        FROM classifier_outputs
        WHERE approved_severity IS NOT NULL
        ORDER BY approved_ts DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def update_approval(record_id, final_severity, notes, approver):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE classifier_outputs
        SET approved_severity = ?,
            approved_corrective_action = ?,
            approved_by = ?,
            approved_ts = ?,
            is_llm_correction_approved = 1
        WHERE id = ?
    """, (final_severity, notes, approver, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), record_id))
    conn.commit()
    conn.close()


# --------------------------
# Approval Dialog
# --------------------------
@st.dialog("Approve Record")
def approval_dialog(record):
    st.write(f"**Payload ID:** {record['payload_id']}")
    st.write(f"**Environment:** {record['environment']}")
    st.write(f"**Current Severity:** {record['Severity']}")
    st.write(f"**Combined Score:** {record['combined_score']}")
    st.write(f"**Corrective Action:** {record['Corrective_Action']}")

    st.divider()

    final_severity = st.selectbox(
        "Final Severity",
        ["Critical", "High", "Medium", "Low"],
        index=["Critical", "High", "Medium", "Low"].index(record['Severity'])
        if record['Severity'] in ["Critical", "High", "Medium", "Low"] else 2
    )

    notes = st.text_area("Approver Notes / Corrective Action", height=100)

    if st.button("Approve", type="primary"):
        approver = st.session_state.get('username', 'admin')
        update_approval(record['id'], final_severity, notes, approver)
        st.success("✅ Record approved and updated in database!")
        st.rerun()


# --------------------------
# Main UI
# --------------------------
def show():
    st.title("🔐 Admin Approvals Dashboard")

    tab1, tab2 = st.tabs(["Pending", "Approved"])

    # --------------------------
    # Pending Tab
    # --------------------------
    with tab1:
        df = get_pending_data()

        if df.empty:
            st.info("🎉 No pending approvals!")
            return

        col1, col2, col3 = st.columns(3)
        col1.metric("Pending", len(df))
        col2.metric("Critical", len(df[df['Severity'] == 'Critical']))
        col3.metric("Avg Score", f"{df['combined_score'].mean():.2f}")

        col1, col2, col3 = st.columns(3)
        env = col1.selectbox("Environment", ["All"] + df['environment'].dropna().unique().tolist())
        sev = col2.selectbox("Severity", ["All"] + df['Severity'].dropna().unique().tolist())
        src = col3.selectbox("Source", ["All"] + df['Source'].dropna().unique().tolist())

        if env != "All":
            df = df[df['environment'] == env]
        if sev != "All":
            df = df[df['Severity'] == sev]
        if src != "All":
            df = df[df['Source'] == src]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "bert_score": st.column_config.NumberColumn("BERT Score", format="%.2f"),
                "rule_score": st.column_config.NumberColumn("Rule Score", format="%.2f"),
                "combined_score": st.column_config.NumberColumn("Combined Score", format="%.2f")
            }
        )

        record_id = st.number_input("Enter ID to approve", min_value=1, step=1)

        if st.button("Approve Record", type="primary"):
            record = df[df['id'] == record_id]
            if not record.empty:
                approval_dialog(record.iloc[0])
            else:
                st.error("Record not found in pending list")

    # --------------------------
    # Approved Tab
    # --------------------------
    with tab2:
        approved_df = get_approved_data()
        if not approved_df.empty:
            st.dataframe(approved_df, use_container_width=True, hide_index=True)
            csv = approved_df.to_csv(index=False).encode('utf-8')
            st.download_button("📥 Export Approved Data", csv, "approved_records.csv", "text/csv")
        else:
            st.info("No approved records yet.")


# Run the app
if __name__ == "__main__":
    show()
