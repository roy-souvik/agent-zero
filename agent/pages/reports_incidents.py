"""
Incidents Report Page with Modal Details
"""
import streamlit as st
from datetime import datetime, timedelta
import random

# Mock data generator
def get_incidents_data():
    severities = ["Critical", "High", "Medium", "Low"]
    statuses = ["Open", "In Progress", "Resolved", "Closed"]
    services = ["api-gateway", "database", "auth-service", "payment-service", "cdn"]

    incidents = []
    for i in range(20):
        severity = random.choice(severities)
        incidents.append({
            "id": f"INC-2024-{1000 + i}",
            "title": random.choice([
                "Database Connection Timeout",
                "High CPU Usage Detected",
                "API Gateway 503 Errors",
                "Memory Leak in Service",
                "Network Latency Spike",
                "Failed Authentication Attempts"
            ]),
            "severity": severity,
            "status": random.choice(statuses),
            "service": random.choice(services),
            "created": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M"),
            "assigned_to": random.choice(["platform-team", "devops-team", "sre-team"]),
            "root_cause": "Connection pool exhaustion due to unoptimized queries",
            "remediation_steps": [
                "Increase database connection pool size",
                "Optimize slow queries",
                "Add connection timeout monitoring",
                "Restart affected services"
            ],
            "metrics": {
                "cpu": random.uniform(50, 95),
                "memory": random.uniform(60, 90),
                "error_rate": random.uniform(1, 20)
            }
        })

    return incidents


def show_incident_modal(incident):
    """Display incident details in modal"""

    modal_html = f"""
    <div class="modal-overlay" onclick="this.style.display='none'">
        <div class="modal-content" onclick="event.stopPropagation()">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 24px;">
                <div>
                    <h2 style="margin: 0; color: white;">{incident['id']}</h2>
                    <p style="color: rgba(255,255,255,0.6); margin: 4px 0 0 0;">{incident['title']}</p>
                </div>
                <span class="status-badge status-{incident['severity'].lower()}">{incident['severity']}</span>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px;">
                <div>
                    <p style="color: rgba(255,255,255,0.5); font-size: 12px; margin: 0;">STATUS</p>
                    <p style="color: white; font-size: 16px; font-weight: 600; margin: 4px 0 0 0;">{incident['status']}</p>
                </div>
                <div>
                    <p style="color: rgba(255,255,255,0.5); font-size: 12px; margin: 0;">SERVICE</p>
                    <p style="color: white; font-size: 16px; font-weight: 600; margin: 4px 0 0 0;">{incident['service']}</p>
                </div>
                <div>
                    <p style="color: rgba(255,255,255,0.5); font-size: 12px; margin: 0;">CREATED</p>
                    <p style="color: white; font-size: 16px; font-weight: 600; margin: 4px 0 0 0;">{incident['created']}</p>
                </div>
                <div>
                    <p style="color: rgba(255,255,255,0.5); font-size: 12px; margin: 0;">ASSIGNED TO</p>
                    <p style="color: white; font-size: 16px; font-weight: 600; margin: 4px 0 0 0;">{incident['assigned_to']}</p>
                </div>
            </div>

            <div style="margin-bottom: 24px;">
                <h3 style="color: white; font-size: 16px; margin-bottom: 12px;">📊 Metrics</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px;">
                    <div class="metric-card">
                        <div class="metric-label">CPU Usage</div>
                        <div class="metric-value">{incident['metrics']['cpu']:.1f}%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Memory</div>
                        <div class="metric-value">{incident['metrics']['memory']:.1f}%</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-label">Error Rate</div>
                        <div class="metric-value">{incident['metrics']['error_rate']:.1f}%</div>
                    </div>
                </div>
            </div>

            <div style="margin-bottom: 24px;">
                <h3 style="color: white; font-size: 16px; margin-bottom: 12px;">🔬 Root Cause</h3>
                <div style="background: rgba(139, 92, 246, 0.1); padding: 16px; border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.3);">
                    <p style="color: white; margin: 0;">{incident['root_cause']}</p>
                </div>
            </div>

            <div>
                <h3 style="color: white; font-size: 16px; margin-bottom: 12px;">🛠️ Remediation Steps</h3>
                <div style="background: rgba(139, 92, 246, 0.05); padding: 16px; border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.2);">
                    {''.join(f'<div style="margin-bottom: 8px;"><span style="color: #8B5CF6; font-weight: 600;">{i+1}.</span> <span style="color: white;">{step}</span></div>' for i, step in enumerate(incident['remediation_steps']))}
                </div>
            </div>

            <div style="margin-top: 24px; text-align: right;">
                <button onclick="this.closest('.modal-overlay').style.display='none'" style="background: #8B5CF6; color: white; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-weight: 600;">Close</button>
            </div>
        </div>
    </div>
    """

    return modal_html


def show():
    st.title("📊 Incidents Report")
    st.markdown("View and analyze all incidents")

    # Filters
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        severity_filter = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"])

    with col2:
        status_filter = st.selectbox("Status", ["All", "Open", "In Progress", "Resolved", "Closed"])

    with col3:
        service_filter = st.selectbox("Service", ["All", "api-gateway", "database", "auth-service", "payment-service", "cdn"])

    with col4:
        date_range = st.selectbox("Date Range", ["Last 7 days", "Last 30 days", "Last 90 days", "All time"])

    st.divider()

    # Get incidents data
    incidents = get_incidents_data()

    # Apply filters
    if severity_filter != "All":
        incidents = [inc for inc in incidents if inc['severity'] == severity_filter]
    if status_filter != "All":
        incidents = [inc for inc in incidents if inc['status'] == status_filter]
    if service_filter != "All":
        incidents = [inc for inc in incidents if inc['service'] == service_filter]

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Total Incidents</div>
            <div class="metric-value">{}</div>
        </div>
        """.format(len(incidents)), unsafe_allow_html=True)

    with col2:
        critical_count = len([i for i in incidents if i['severity'] == 'Critical'])
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Critical</div>
            <div class="metric-value" style="color: #EF4444;">{}</div>
        </div>
        """.format(critical_count), unsafe_allow_html=True)

    with col3:
        open_count = len([i for i in incidents if i['status'] in ['Open', 'In Progress']])
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Open/In Progress</div>
            <div class="metric-value" style="color: #FB923C;">{}</div>
        </div>
        """.format(open_count), unsafe_allow_html=True)

    with col4:
        resolved_count = len([i for i in incidents if i['status'] in ['Resolved', 'Closed']])
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Resolved</div>
            <div class="metric-value" style="color: #22C55E;">{}</div>
        </div>
        """.format(resolved_count), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Incidents list
    st.subheader("Recent Incidents")

    # Use session state to track selected incident
    if 'selected_incident' not in st.session_state:
        st.session_state.selected_incident = None

    for incident in incidents:
        # Create card
        card_html = f"""
        <div class="incident-card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
                <div style="flex: 1;">
                    <h3 style="color: white; font-size: 18px; margin: 0 0 4px 0;">{incident['id']}</h3>
                    <p style="color: rgba(255,255,255,0.7); font-size: 14px; margin: 0;">{incident['title']}</p>
                </div>
                <span class="status-badge status-{incident['severity'].lower()}">{incident['severity']}</span>
            </div>

            <div style="display: flex; gap: 24px; color: rgba(255,255,255,0.5); font-size: 13px;">
                <span>🏷️ {incident['service']}</span>
                <span>👥 {incident['assigned_to']}</span>
                <span>🕒 {incident['created']}</span>
                <span>📊 {incident['status']}</span>
            </div>
        </div>
        """

        st.markdown(card_html, unsafe_allow_html=True)

        # Add button to view details
        if st.button("View Details", key=f"btn_{incident['id']}"):
            st.session_state.selected_incident = incident

    # Show modal if incident is selected
    if st.session_state.selected_incident:
        modal_html = show_incident_modal(st.session_state.selected_incident)
        st.markdown(modal_html, unsafe_allow_html=True)

        # Add a button to close modal
        if st.button("Close Modal", key="close_modal"):
            st.session_state.selected_incident = None
            st.rerun()