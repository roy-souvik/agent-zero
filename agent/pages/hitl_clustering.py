# pip install anthropic streamlit scikit-learn pandas plotly numpy

import json
import sqlite3
import numpy as np
import pandas as pd
import streamlit as st
from datetime import datetime
from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.decomposition import PCA
import plotly.express as px
from anthropic import Anthropic

# Initialize Streamlit page config
st.set_page_config(page_title="Clustering Agent", layout="wide")

# Database setup
def init_db():
    conn = sqlite3.connect("clustering_agent.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clustering_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            algorithm TEXT,
            config TEXT,
            silhouette_score REAL,
            davies_bouldin_score REAL,
            human_rating INTEGER,
            human_feedback TEXT,
            data_hash TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            selected_result_id INTEGER,
            reason TEXT,
            learning_data TEXT
        )
    """)
    conn.commit()
    return conn

# Load feedback history for agent learning
def get_agent_feedback_history(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT learning_data FROM agent_feedback ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()
    return [json.loads(row[0]) for row in rows if row[0]]

# Save clustering result
def save_clustering_result(conn, algorithm, config, silhouette, davies_bouldin, data_hash):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO clustering_results
        (timestamp, algorithm, config, silhouette_score, davies_bouldin_score, data_hash)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.now().isoformat(), algorithm, json.dumps(config), silhouette, davies_bouldin, data_hash))
    conn.commit()
    return cursor.lastrowid

# Save human feedback
def save_human_feedback(conn, result_id, rating, feedback, learning_data):
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE clustering_results
        SET human_rating = ?, human_feedback = ?
        WHERE id = ?
    """, (rating, feedback, result_id))
    cursor.execute("""
        INSERT INTO agent_feedback (timestamp, selected_result_id, reason, learning_data)
        VALUES (?, ?, ?, ?)
    """, (datetime.now().isoformat(), result_id, feedback, json.dumps(learning_data)))
    conn.commit()

# Generate synthetic data or load from user
def load_data():
    st.sidebar.title("Data Input")
    option = st.sidebar.radio("Choose data source:", ["Upload CSV", "Generate Synthetic"])

    if option == "Upload CSV":
        file = st.sidebar.file_uploader("Upload CSV", type="csv")
        if file:
            data = pd.read_csv(file)
            return data
    else:
        n_samples = st.sidebar.slider("Number of samples:", 100, 1000, 300)
        n_features = st.sidebar.slider("Number of features:", 2, 10, 5)
        data = pd.DataFrame(np.random.randn(n_samples, n_features),
                          columns=[f"feature_{i}" for i in range(n_features)])
        st.sidebar.success(f"Generated {n_samples} samples with {n_features} features")
        return data

    return None

# Clustering execution
def run_clustering(data, algorithm, config):
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(data)

    if algorithm == "kmeans":
        model = KMeans(n_clusters=config["n_clusters"], random_state=42, n_init=10)
    elif algorithm == "dbscan":
        model = DBSCAN(eps=config["eps"], min_samples=config["min_samples"])
    elif algorithm == "hierarchical":
        model = AgglomerativeClustering(n_clusters=config["n_clusters"],
                                       linkage=config["linkage"])

    labels = model.fit_predict(X_scaled)

    # Calculate metrics
    if len(np.unique(labels)) > 1:
        silhouette = silhouette_score(X_scaled, labels)
        davies_bouldin = davies_bouldin_score(X_scaled, labels)
    else:
        silhouette = -1
        davies_bouldin = -1

    return labels, X_scaled, silhouette, davies_bouldin

# Agent orchestration with Claude
def run_agent(data, conn, previous_feedback):
    client = Anthropic()

    # Build context from learning history
    feedback_context = "Previous successful configurations:" if previous_feedback else "First run."
    for fb in previous_feedback[:3]:
        feedback_context += f"\n- Algorithm: {fb.get('algorithm')}, Config: {fb.get('config')}, Rating: {fb.get('rating')}"

    prompt = f"""You are a clustering expert agent. Based on the data shape {data.shape} and previous feedback:
{feedback_context}

Recommend 3 different clustering configurations to try. For each, specify:
1. Algorithm (kmeans, dbscan, hierarchical)
2. Configuration parameters
3. Why it might work well

Format your response as JSON array with objects containing: algorithm, config (dict), reason"""

    message = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text

    # Parse JSON from response
    try:
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        configs = json.loads(response_text[start:end])
        return configs
    except:
        # Fallback configurations
        return [
            {"algorithm": "kmeans", "config": {"n_clusters": 3}, "reason": "Basic clustering"},
            {"algorithm": "kmeans", "config": {"n_clusters": 5}, "reason": "More clusters"},
            {"algorithm": "dbscan", "config": {"eps": 0.5, "min_samples": 5}, "reason": "Density-based"}
        ]

# Visualization
def visualize_clustering(X_scaled, labels, title):
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    df_viz = pd.DataFrame(X_pca, columns=["PC1", "PC2"])
    df_viz["Cluster"] = labels.astype(str)

    fig = px.scatter(df_viz, x="PC1", y="PC2", color="Cluster",
                    title=title, hover_data={"Cluster": True})
    return fig

# Main app
st.title("🤖 Human-in-the-Loop Clustering Agent")

conn = init_db()

# Load data
data = load_data()

if data is not None:
    st.write(f"Data shape: {data.shape}")

    # Run agent
    if st.button("🚀 Run Agent & Generate Configurations"):
        previous_feedback = get_agent_feedback_history(conn)

        with st.spinner("Agent thinking..."):
            configs = run_agent(data, conn, previous_feedback)

        st.session_state.configs = configs
        st.session_state.data = data
        st.success("Agent generated 3 configurations!")

    # Display and evaluate results
    if "configs" in st.session_state:
        data_hash = str(hash(tuple(st.session_state.data.values.flatten())))
        results = []

        st.subheader("Clustering Results")
        cols = st.columns(3)

        for idx, config_obj in enumerate(st.session_state.configs):
            with cols[idx]:
                st.write(f"**{config_obj['algorithm'].upper()}**")
                st.caption(config_obj.get("reason", ""))

                with st.spinner(f"Running {config_obj['algorithm']}..."):
                    labels, X_scaled, silhouette, davies_bouldin = run_clustering(
                        st.session_state.data,
                        config_obj["algorithm"],
                        config_obj["config"]
                    )

                result_id = save_clustering_result(
                    conn, config_obj["algorithm"], config_obj["config"],
                    silhouette, davies_bouldin, data_hash
                )

                st.metric("Silhouette Score", f"{silhouette:.3f}")
                st.metric("Davies-Bouldin Index", f"{davies_bouldin:.3f}")

                fig = visualize_clustering(X_scaled, labels, f"{config_obj['algorithm']} Clustering")
                st.plotly_chart(fig, use_container_width=True)

                if st.button(f"✅ Select This", key=f"select_{idx}"):
                    st.session_state.selected_result = {
                        "id": result_id,
                        "algorithm": config_obj["algorithm"],
                        "config": config_obj["config"],
                        "silhouette": silhouette,
                        "davies_bouldin": davies_bouldin
                    }

        # Human feedback section
        if "selected_result" in st.session_state:
            st.subheader("📋 Your Feedback")
            rating = st.slider("Rate this clustering (1-5):", 1, 5, 4)
            feedback = st.text_area("Why did you choose this clustering?")

            if st.button("💾 Save Feedback & Update Agent"):
                learning_data = {
                    "algorithm": st.session_state.selected_result["algorithm"],
                    "config": st.session_state.selected_result["config"],
                    "rating": rating,
                    "feedback": feedback
                }
                save_human_feedback(
                    conn,
                    st.session_state.selected_result["id"],
                    rating,
                    feedback,
                    learning_data
                )
                st.success("✅ Feedback saved! Agent will learn from this.")
                st.balloons()