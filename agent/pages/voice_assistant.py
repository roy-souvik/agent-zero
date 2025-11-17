import streamlit as st
import speech_recognition as sr
import requests
import os
import tempfile
from dotenv import load_dotenv
from gtts import gTTS

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")


# ---------------------------------------
# Helper Functions
# ---------------------------------------

def transcribe_audio(audio_bytes: bytes):
    r = sr.Recognizer()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        f.flush()

        try:
            with sr.AudioFile(f.name) as source:
                audio = r.record(source)
                return r.recognize_google(audio)
        except:
            return None


def ask_ollama(text: str) -> str:
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
    tts = gTTS(text)
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        tts.save(f.name)
        audio_path = f.name

    audio_bytes = open(audio_path, "rb").read()

    # Autoplay in Streamlit
    st.audio(audio_bytes, format="audio/mp3", autoplay=True)


# ---------------------------------------
# Streamlit UI
# ---------------------------------------

def show():
    st.set_page_config(page_title="Voice Assistant", page_icon="🎙️")
    st.title("🎙️ Incident Management Voice Assistant")
    st.markdown("Speak once. After you stop recording, everything happens automatically.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    st.subheader("🎤 Record Your Voice")
    audio_data = st.audio_input("Click to record your question")

    # RUN PIPELINE AUTOMATICALLY ONCE per recording
    if audio_data and "last_audio" not in st.session_state:
        st.session_state.last_audio = True  # prevent re-trigger
        audio_bytes = audio_data.read()

        with st.spinner("Transcribing..."):
            user_text = transcribe_audio(audio_bytes)

        if not user_text:
            st.error("Could not understand audio.")
        else:
            st.session_state.messages.append({"role": "user", "content": user_text})
            st.success(f"You said: **{user_text}**")

            with st.spinner("AI thinking..."):
                ai_response = ask_ollama(user_text)

            st.session_state.messages.append({"role": "assistant", "content": ai_response})

            speak_text(ai_response)
            st.info("🔊 Assistant is speaking...")

        # cleanup trigger — allow next recording to run again
        st.session_state.last_audio = None

    # Conversation History
    st.markdown("---")
    st.subheader("💬 Conversation")

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    st.markdown("---")
    st.subheader("⌨️ Type instead")

    if user_prompt := st.chat_input("Ask something…"):
        st.session_state.messages.append({"role": "user", "content": user_prompt})

        with st.spinner("AI thinking..."):
            ai_response = ask_ollama(user_prompt)

        st.session_state.messages.append({"role": "assistant", "content": ai_response})
        speak_text(ai_response)

    if st.button("🗑️ Clear Conversation"):
        st.session_state.messages = []
        st.session_state.last_audio = None
        st.rerun()