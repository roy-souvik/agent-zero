"""
Alerts Report Page
"""
import streamlit as st
from datetime import datetime, timedelta
import random

def get_alerts_data():
    alert_types = ["High CPU", "Memory Leak", "Disk Space", "Network Latency", "Error Rate", "Timeout"]
    severities = ["Critical", "High", "Medium", "Low"]
    sources = ["Prometheus", "Datadog", "CloudWatch", "New Relic", "Custom Monitor"]

    alerts = []
    for i in range(30):
        alerts.append({
            "id": f"ALT-{10000 + i}",
            "type": random.choice(alert_types),
            "severity": random.choice(severities),
            "source": random.choice(sources),
            "triggered": (datetime.now() - timedelta(hours=random.randint(0, 72))).strftime("%Y-%m-%d %H:%M"),
            "status": random.choice(["Active", "Acknowledged", "Resolved"]),
            "threshold": f"{random.uniform(70, 95):.1f}%",
            "current_value": f"{random.uniform(75, 99):.1f}%",
            "message": "Alert threshold exceeded for extended period"
        })

    return alerts


def show():
    st.title("🔔 Alerts Report")
    st.markdown("Monitor and manage system alerts")

    # Filters
    col1, col2, col3 = st.columns(3)

    with col1:
        severity_filter = st.selectbox("Severity", ["All", "Critical", "High", "Medium", "Low"], key="alert_sev")

    with col2:
        status_filter = st.selectbox("Status", ["All", "Active", "Acknowledged", "Resolved"], key="alert_status")

    with col3:
        source_filter = st.selectbox("Source", ["All", "Prometheus", "Datadog", "CloudWatch", "New Relic", "Custom Monitor"], key="alert_source")

    st.divider()

    # Get alerts
    alerts = get_alerts_data()

    # Apply filters
    if severity_filter != "All":
        alerts = [a for a in alerts if a['severity'] == severity_filter]
    if status_filter != "All":
        alerts = [a for a in alerts if a['status'] == status_filter]
    if source_filter != "All":
        alerts = [a for a in alerts if a['source'] == source_filter]

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Total Alerts</div>
            <div class="metric-value">{len(alerts)}</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        active = len([a for a in alerts if a['status'] == 'Active'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Active</div>
            <div class="metric-value" style="color: #EF4444;">{active}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        ack = len([a for a in alerts if a['status'] == 'Acknowledged'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Acknowledged</div>
            <div class="metric-value" style="color: #FB923C;">{ack}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        resolved = len([a for a in alerts if a['status'] == 'Resolved'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Resolved</div>
            <div class="metric-value" style="color: #22C55E;">{resolved}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Alerts list
    st.subheader("Active Alerts")

    for alert in alerts:
        card_html = f"""
        <div class="incident-card">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
                        <h3 style="color: white; font-size: 16px; margin: 0;">{alert['type']}</h3>
                        <span class="status-badge status-{alert['severity'].lower()}">{alert['severity']}</span>
                    </div>
                    <p style="color: rgba(255,255,255,0.6); font-size: 13px; margin: 0 0 12px 0;">{alert['message']}</p>
                    <div style="display: flex; gap: 20px; color: rgba(255,255,255,0.5); font-size: 12px;">
                        <span>📡 {alert['source']}</span>
                        <span>🎯 Threshold: {alert['threshold']}</span>
                        <span>📊 Current: {alert['current_value']}</span>
                        <span>🕒 {alert['triggered']}</span>
                    </div>
                </div>
                <div style="display: flex; gap: 8px;">
                    <span style="background: {'rgba(34, 197, 94, 0.2)' if alert['status'] == 'Resolved' else 'rgba(251, 146, 60, 0.2)'}; color: {'#22C55E' if alert['status'] == 'Resolved' else '#FB923C'}; padding: 6px 12px; border-radius: 8px; font-size: 12px; font-weight: 600;">{alert['status']}</span>
                </div>
            </div>
        </div>
        """

        st.markdown(card_html, unsafe_allow_html=True)