# import streamlit as st
# from dotenv import load_dotenv
# from agent import agent

# load_dotenv()
# st.set_page_config(page_title="LangChain AI Agent", layout="centered")

# st.title("LangChain + Ollama + Chroma AI Agent")

# st.sidebar.header("📘 Memory")
# new_text = st.sidebar.text_area("Add a document to memory:")

# query = st.text_input("Ask something:")
# if st.button("Run Agent"):
#     if query.strip():
#         with st.spinner("The AI is Thinking..."):
#             result = agent.invoke({"input": query})
#         st.write("### 🤖 Response:")
#         st.write(result if isinstance(result, str) else result.get("output", result))
#     else:
#         st.warning("Please enter a question.")


import streamlit as st
from dotenv import load_dotenv
from agent import run_agent

load_dotenv()

st.set_page_config(page_title="LangChain + Ollama", layout="centered")
st.title("🧩 LangChain + Ollama (Direct Mode)")

query = st.text_input("Ask something:")
if st.button("Run Agent"):
    if query.strip():
        with st.spinner("The AI is thinking..."):
            response = run_agent(query)
        st.write("### 🤖 Response:")
        st.write(response)
    else:
        st.warning("Please enter a question.")
