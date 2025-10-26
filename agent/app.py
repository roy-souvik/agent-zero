import streamlit as st
from agent import agent

st.title("🧠 Local AI Agent with Chroma + Ollama")

query = st.text_input("Ask me something:")
if st.button("Run Agent") and query:
    with st.spinner("Thinking..."):
        result = agent.invoke({"input": query})
    st.success(result["output"])