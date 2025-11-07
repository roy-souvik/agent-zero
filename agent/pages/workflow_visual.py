import streamlit as st
import time

def show():
    st.set_page_config(layout="wide")
    st.title("⚙️ Cloud AI Agent Workflow")

    st.markdown("""
    <style>
    .flow {
        display: flex; justify-content: center; align-items: center;
        gap: 60px; margin-top: 60px; flex-wrap: nowrap; overflow-x: auto;
    }
    .box {
        width: 260px; height: 200px; border-radius: 15px;
        background: linear-gradient(145deg,#1f2937,#111827);
        color: white; text-align: center;
        display: flex; flex-direction: row; justify-content: center;
        box-shadow: 8px 8px 20px #0f172a, -4px -4px 10px #334155;
        font-weight: 600; padding: 10px; transition: all .3s ease;
    }
    .active {
        border: 3px solid #22c55e;
        box-shadow: 0 0 25px #22c55e, inset 0 0 10px #22c55e;
        animation: pulse 1.5s infinite alternate;
    }
    @keyframes pulse { from { transform: scale(1); } to { transform: scale(1.05); } }
    .connector {
        width: 80px; height: 4px;
        background: linear-gradient(90deg,#22c55e,#16a34a,#22c55e);
        border-radius: 2px;
        animation: flow 1s infinite alternate;
    }
    @keyframes flow { from{opacity:.3;} to{opacity:1;} }
    .logbox {
        background:#0a0a0a; color:#9ca3af; font-size:13px;
        padding:10px; border-radius:8px; margin-top:5px;
        font-family: monospace;
    }
    </style>
    """, unsafe_allow_html=True)

    steps = [
        {"name":"📥 Data Ingestion","info":"Collect and validate raw input data","note":"Ensures schema and quality checks"},
        {"name":"⚙️ Data Processing","info":"Clean and transform structured data","note":"ETL tasks and feature extraction"},
        {"name":"🧠 Model Training","info":"Train ML models using updated data","note":"Hyperparameter tuning in progress"},
        {"name":"🚨 Alert Generation","info":"Detect anomalies and issue alerts","note":"Real-time incident scoring"},
        {"name":"📊 Report Summary","info":"Generate insights and reports","note":"Exports dashboards and summaries"},
    ]

    if st.button("▶️ Start Workflow"):
        placeholder = st.empty()
        for i, step in enumerate(steps):
            with placeholder.container():
                st.markdown('<div class="flow">', unsafe_allow_html=True)
                for j, s in enumerate(steps):
                    cls = "box active" if j == i else "box"
                    st.markdown(f"""
                    <div class="{cls}">
                        <div style="font-size:24px;">{s["name"]}</div>
                        <div style="font-size:14px;margin-top:6px;color:#d1d5db;">{s["info"]}</div>
                        <div style="font-size:12px;margin-top:10px;color:#a5b4fc;">💡 {s["note"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if j < len(steps)-1:
                        st.markdown('<div class="connector"></div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                with st.expander(f"🔍 Logs for {step['name']}"):
                    for k in range(1, 4):
                        st.markdown(f'<div class="logbox">[{time.strftime("%H:%M:%S")}] Step {i+1}: Log entry {k}...</div>', unsafe_allow_html=True)
                        time.sleep(0.4)
            time.sleep(1)

        st.success("✅ Workflow completed successfully!")
        st.balloons()
