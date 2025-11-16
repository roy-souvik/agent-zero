"""
Streamlit Voice Assistant
"""
import streamlit as st
import speech_recognition as sr
import requests
import os
from io import BytesIO
import tempfile

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

def transcribe_audio(audio_bytes):
    """Transcribe audio to text"""
    r = sr.Recognizer()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        f.flush()

        with sr.AudioFile(f.name) as source:
            audio = r.record(source)
            try:
                return r.recognize_google(audio)
            except:
                return None

def ask_ollama(text):
    """Query Ollama"""
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": f"You are an incident management assistant. Be brief. User: {text}",
            "stream": False
        },
        timeout=30
    )
    return resp.json()["response"]

def show():
    st.title("🎙️ Voice Assistant")

    if "voice_messages" not in st.session_state:
        st.session_state.voice_messages = []

    # Audio recorder
    st.markdown("### Record Your Question")

    audio_bytes = st.audio_input("Click to record")

    if audio_bytes:
        if st.button("📝 Transcribe & Send", type="primary"):
            with st.spinner("Transcribing..."):
                text = transcribe_audio(audio_bytes.read())

                if text:
                    st.success(f"You: {text}")
                    st.session_state.voice_messages.append({"role": "user", "content": text})

                    with st.spinner("AI thinking..."):
                        response = ask_ollama(text)
                        st.session_state.voice_messages.append({"role": "assistant", "content": response})

                    st.rerun()
                else:
                    st.error("Could not understand audio")

    # Chat history
    st.markdown("---")
    st.markdown("### Conversation")

    for msg in st.session_state.voice_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # Text input fallback
    if prompt := st.chat_input("Or type your question..."):
        st.session_state.voice_messages.append({"role": "user", "content": prompt})

        with st.spinner("Thinking..."):
            response = ask_ollama(prompt)
            st.session_state.voice_messages.append({"role": "assistant", "content": response})

        st.rerun()

    if st.button("Clear Chat"):
        st.session_state.voice_messages = []
        st.rerun()