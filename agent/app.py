import streamlit as st
from dotenv import load_dotenv
from agent import agent

load_dotenv()

st.set_page_config(page_title="LangChain AI Agent", layout="centered")

st.title("🧩 LangChain + Ollama + Chroma AI Agent")

# Sidebar for document addition
st.sidebar.header("📘 Memory")
new_text = st.sidebar.text_area("Add a document to memory:")

# Chat UI
query = st.text_input("💬 Ask something:")
if st.button("Run Agent"):
    if query.strip():
        with st.spinner("Thinking..."):
            result = agent.invoke({"input": query})
        st.write("### 🤖 Response:")
        st.write(result)
    else:
        st.warning("Please enter a question.")

# Optional: show similar docs
if query.strip():
    with st.expander("🔍 Retrieved Context"):
        docs = vectorstore.similarity_search(query, k=2)
        if docs:
            for d in docs:
                st.write("-", d.page_content)
        else:
            st.write("No context found.")
