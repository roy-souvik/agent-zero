"""
Streamlit Voice Assistant (Live Listen + Speak)
Combines logic from the console-based assistant with the Streamlit reference.
"""

import streamlit as st
import speech_recognition as sr
import requests
import os
import tempfile
import threading
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")


# ------------------------------
# Helper Functions
# ------------------------------

def transcribe_audio(audio_bytes: bytes):
    """Convert audio bytes to text using Google Speech Recognition."""
    r = sr.Recognizer()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        f.flush()

        try:
            with sr.AudioFile(f.name) as source:
                audio = r.record(source)
                return r.recognize_google(audio)
        except Exception:
            return None


def ask_ollama(text: str) -> str:
    """Query Ollama model and return the response."""
    try:
        resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": f"You are an incident management assistant. Be brief and conversational. User: {text}",
                "stream": False
            },
            timeout=30
        )
        return resp.json().get("response", "I couldn't generate a response.")
    except Exception as e:
        return f"Error communicating with AI model: {e}"

def speak_text(text):
    # Create audio file
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tts.save(f.name)
        audio_path = f.name

    # Streamlit plays audio in browser (no ALSA required)
    audio_bytes = open(audio_path, "rb").read()
    st.audio(audio_bytes, format="audio/mp3")

# ------------------------------
# Streamlit UI
# ------------------------------

def show():
    st.set_page_config(page_title="Voice Assistant", page_icon="🎙️")
    st.title("🎙️ Incident Management Voice Assistant")
    st.markdown("Speak or type your question. The assistant will respond and talk back.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # ---------------------------------------
    # AUDIO RECORDING SECTION
    # ---------------------------------------
    st.subheader("🎤 Record Your Voice")
    audio_data = st.audio_input("Click to record your question")

    if audio_data:
        if st.button("📝 Transcribe & Ask", type="primary", use_container_width=True):
            with st.spinner("Transcribing audio..."):
                user_text = transcribe_audio(audio_data.read())

            if user_text:
                st.success(f"You said: **{user_text}**")
                st.session_state.messages.append({"role": "user", "content": user_text})

                with st.spinner("AI thinking..."):
                    ai_response = ask_ollama(user_text)
                    st.session_state.messages.append({"role": "assistant", "content": ai_response})

                speak_text(ai_response)
                st.info("🔊 Assistant is speaking...")
                st.rerun()
            else:
                st.error("Could not understand audio.")

    # ---------------------------------------
    # CHAT HISTORY
    # ---------------------------------------
    st.markdown("---")
    st.subheader("💬 Conversation")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

            if msg["role"] == "assistant":
                if st.button("🔊 Play", key=f"play_{hash(msg['content'])}"):
                    speak_text(msg["content"])
                    st.info("Speaking...")

    if not st.session_state.messages:
        st.info("No messages yet. Start by recording or typing!")

    # ---------------------------------------
    # TEXT INPUT SECTION
    # ---------------------------------------
    st.markdown("---")
    st.subheader("⌨️ Or Type Your Question")

    if user_prompt := st.chat_input("Type your question here…"):
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.spinner("AI thinking..."):
            ai_response = ask_ollama(user_prompt)
            st.session_state.messages.append({"role": "assistant", "content": ai_response})

        speak_text(ai_response)
        st.rerun()

    # ---------------------------------------
    # CLEAR CHAT
    # ---------------------------------------
    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.rerun()