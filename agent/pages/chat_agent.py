import streamlit as st

def show():
    st.title("💬 Chat Agent")
    st.markdown("*Coming soon...*")
    st.info("This will be a conversational AI agent")

    # Placeholder for future chat interface
    st.text_input("Message:", placeholder="Type your message here...", disabled=True)
    st.button("Send", disabled=True)