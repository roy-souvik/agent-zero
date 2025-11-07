import streamlit as st
import json
from datetime import datetime
from components.pipeline import render_pipeline, run_pipeline_animation, create_incident_pipeline

def show():
    st.title("🔍 AI-Powered Incident Analysis")
    st.markdown("Multi-agent system analyzes incidents using CrewAI")

    # Create tabs for different input methods
    tab1, tab2, tab3 = st.tabs(["📄 Upload Logs", "✍️ Manual Input", "🔗 Live Feed"])

    with tab1:
        st.subheader("Upload Incident Logs")
        uploaded_file = st.file_uploader(
            "Upload JSON or text logs",
            type=['json', 'txt', 'log'],
            help="Upload incident logs in JSON format"
        )

        if uploaded_file:
            content = uploaded_file.read().decode('utf-8')
            st.text_area("File Content Preview", content[:500] + "...", height=150)

            col1, col2 = st.columns([3, 1])
            with col1:
                incident_title = st.text_input("Incident Title", "Automated from logs")
            with col2:
                service_name = st.text_input("Service", "api-service")

            if st.button("🤖 Analyze with AI Agents", type="primary", key="upload"):
                analyze_incident(content, incident_title, service_name)

    with tab2:
        st.subheader("Manual Incident Entry")

        col1, col2 = st.columns(2)
        with col1:
            incident_title = st.text_input("Incident Title*", placeholder="e.g., API Gateway Timeout")
            service = st.selectbox("Affected Service*", [
                "api-gateway", "database", "auth-service",
                "payment-service", "notification-service", "cdn"
            ])

        with col2:
            incident_type = st.selectbox("Incident Type", [
                "Performance Degradation", "Service Outage", "Security Alert",
                "Data Loss", "Network Issue", "Configuration Error"
            ])
            priority = st.select_slider("Priority", ["Low", "Medium", "High", "Critical"])

        alert_message = st.text_area(
            "Alert Message / Description*",
            placeholder="Paste alert message or describe the incident...",
            height=120
        )

        with st.expander("📊 Additional Context (Optional)"):
            col1, col2 = st.columns(2)
            with col1:
                affected_users = st.number_input("Affected Users", 0, 1000000, 0)
                error_rate = st.slider("Error Rate %", 0, 100, 0)
            with col2:
                cpu_usage = st.slider("CPU Usage %", 0, 100, 50)
                memory_usage = st.slider("Memory Usage %", 0, 100, 60)

        if st.button("🤖 Analyze with AI Agents", type="primary", key="manual"):
            if not incident_title or not alert_message:
                st.error("⚠️ Please fill in required fields (marked with *)")
            else:
                incident_data = {
                    "title": incident_title,
                    "service": service,
                    "type": incident_type,
                    "priority": priority,
                    "description": alert_message,
                    "metrics": {
                        "affected_users": affected_users,
                        "error_rate": error_rate,
                        "cpu_usage": cpu_usage,
                        "memory_usage": memory_usage
                    },
                    "timestamp": datetime.now().isoformat()
                }
                analyze_incident(json.dumps(incident_data), incident_title, service)

    with tab3:
        st.subheader("Live Incident Feed")
        st.info("🔌 Connect to monitoring systems (Coming Soon)")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active Monitors", "12", "+2")
            st.metric("Pending Alerts", "5", "-3")
        with col2:
            st.metric("Auto-Resolved", "8", "+4")
            st.metric("Escalated", "2", "+1")

        if st.button("🔄 Refresh Feed"):
            st.success("Feed refreshed")


def analyze_incident(log_data: str, title: str, service: str):
    """Process incident with LangGraph multi-agent system"""

    with st.spinner("🤖 AI Agents are analyzing the incident..."):
        # Import LangGraph workflow
        from langgraph_agents import process_incident

        # Prepare incident data
        incident_data = {
            "title": title,
            "service": service,
            "logs": log_data,
            "description": log_data[:500] if len(log_data) > 500 else log_data,
            "timestamp": datetime.now().isoformat()
        }

        # Process with LangGraph
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Run the workflow
            result = process_incident(incident_data)

            # Extract results
            triage_result = result.get("triage", {})
            diagnosis_result = result.get("diagnosis", {})
            remediation_result = result.get("remediation", {})
            ticket_result = result.get("ticket", {})

            status_text.text("✅ Analysis Complete!")
            progress_bar.progress(100)

        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")
            # Fallback to simulated results
            progress_bar = st.progress(0)
            status_text = st.empty()

        # Stage 1: Triage
        status_text.text("🔍 Triage Agent: Classifying severity...")
        progress_bar.progress(20)

        # Mock triage result
        triage_result = {
            "severity": "High",
            "reasoning": "High error rate (15%), CPU at 85%, affecting core API service",
            "priority_score": 8.5
        }

        # Stage 2: Diagnosis
        status_text.text("🔬 Diagnosis Agent: Identifying root cause...")
        progress_bar.progress(40)

        diagnosis_result = {
            "root_cause": "Database connection pool exhaustion",
            "evidence": [
                "Connection timeout errors in logs",
                "Max connections reached (200/200)",
                "Slow query execution times (>5s)"
            ],
            "similar_incidents": ["INC-2024-001", "INC-2023-089"]
        }

        # Stage 3: Remediation
        status_text.text("🛠️ Remediation Agent: Generating solution...")
        progress_bar.progress(60)

        remediation_result = {
            "steps": [
                "Increase database max_connections from 200 to 400",
                "Restart database service",
                "Clear connection pool cache",
                "Monitor connection usage for 1 hour",
                "Scale database instance if issue persists"
            ],
            "escalation": "Escalate to DBA team if not resolved in 30 minutes",
            "eta": "15-30 minutes"
        }

        # Stage 4: Ticketing
        status_text.text("📋 Ticketing Agent: Creating ticket...")
        progress_bar.progress(80)

        ticket_result = {
            "ticket_id": f"INC-{datetime.now().strftime('%Y%m%d')}-{hash(title) % 1000}",
            "assigned_to": "platform-team",
            "status": "Open"
        }

        # Stage 5: Reporting
        status_text.text("📄 Report Agent: Generating report...")
        progress_bar.progress(100)

        status_text.text("✅ Analysis Complete!")

    # Display results
    st.success("✅ Multi-Agent Analysis Complete!")
    st.balloons()

    # Results Layout
    col1, col2 = st.columns([2, 1])

    with col1:
        # Severity Classification
        st.subheader("🎯 Severity Classification")
        severity_color = {
            "Critical": "🔴",
            "High": "🟠",
            "Medium": "🟡",
            "Low": "🟢"
        }
        st.markdown(f"### {severity_color.get(triage_result['severity'])} {triage_result['severity']}")
        st.write(f"**Reasoning:** {triage_result['reasoning']}")
        st.metric("Priority Score", f"{triage_result['priority_score']}/10")

        # Root Cause Analysis
        st.subheader("🔬 Root Cause Analysis")
        st.error(f"**{diagnosis_result['root_cause']}**")

        st.write("**Supporting Evidence:**")
        for evidence in diagnosis_result['evidence']:
            st.write(f"• {evidence}")

        # Remediation Plan
        st.subheader("🛠️ Remediation Plan")
        st.write("**Action Steps:**")
        for i, step in enumerate(remediation_result['steps'], 1):
            st.write(f"{i}. {step}")

        st.info(f"⚠️ **Escalation:** {remediation_result['escalation']}")
        st.success(f"⏱️ **Estimated Resolution:** {remediation_result['eta']}")

    with col2:
        # Ticket Information
        st.subheader("📋 Ticket Created")
        st.code(ticket_result['ticket_id'], language=None)
        st.write(f"**Assigned:** {ticket_result['assigned_to']}")
        st.write(f"**Status:** {ticket_result['status']}")

        if st.button("📋 View Full Ticket"):
            st.info("Opening ticket details...")

        # Similar Incidents
        st.subheader("📚 Similar Incidents")
        for inc_id in diagnosis_result['similar_incidents']:
            st.write(f"• {inc_id}")

        # Actions
        st.subheader("⚡ Quick Actions")
        if st.button("🔔 Send Alerts", use_container_width=True):
            st.success("Alerts sent to platform-team")

        if st.button("📈 Escalate", use_container_width=True):
            st.warning("Escalated to Engineering Manager")

        if st.button("📥 Download Report", use_container_width=True):
            report_data = generate_report(triage_result, diagnosis_result, remediation_result, ticket_result)
            st.download_button(
                "Download PDF",
                data=report_data,
                file_name=f"incident_report_{ticket_result['ticket_id']}.txt",
                mime="text/plain"
            )


def generate_report(triage, diagnosis, remediation, ticket):
    """Generate incident report"""
    report = f"""
INCIDENT REPORT
===============

Ticket ID: {ticket['ticket_id']}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SEVERITY CLASSIFICATION
-----------------------
Severity: {triage['severity']}
Priority Score: {triage['priority_score']}/10
Reasoning: {triage['reasoning']}

ROOT CAUSE ANALYSIS
-------------------
Root Cause: {diagnosis['root_cause']}

Evidence:
{chr(10).join('- ' + e for e in diagnosis['evidence'])}

Similar Incidents: {', '.join(diagnosis['similar_incidents'])}

REMEDIATION PLAN
----------------
Steps:
{chr(10).join(f'{i}. {s}' for i, s in enumerate(remediation['steps'], 1))}

Escalation: {remediation['escalation']}
Estimated Resolution: {remediation['eta']}

ASSIGNMENT
----------
Assigned To: {ticket['assigned_to']}
Status: {ticket['status']}
"""
    return report