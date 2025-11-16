"""
Simple Voice Agent with Ollama
"""
import logging
import requests
import os
from dotenv import load_dotenv
import speech_recognition as sr
import pyttsx3

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

logging.basicConfig(level=logging.INFO)

def main():
    r = sr.Recognizer()
    tts = pyttsx3.init()
    tts.setProperty('rate', 150)

    print("Voice Assistant Started. Say 'exit' to quit.")
    tts.say("Hello! I'm your incident management assistant. How can I help?")
    tts.runAndWait()

    while True:
        try:
            with sr.Microphone() as source:
                print("\nListening...")
                r.adjust_for_ambient_noise(source, duration=0.5)
                audio = r.listen(source, timeout=5)

            print("Recognizing...")
            text = r.recognize_google(audio)
            print(f"You: {text}")

            if "exit" in text.lower() or "quit" in text.lower():
                tts.say("Goodbye!")
                tts.runAndWait()
                break

            # Ask Ollama
            print("Thinking...")
            resp = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": f"You are an incident management assistant. Be brief and conversational. User: {text}",
                    "stream": False
                },
                timeout=30
            )

            answer = resp.json()["response"]
            print(f"AI: {answer}")

            # Speak response
            tts.say(answer)
            tts.runAndWait()

        except sr.WaitTimeoutError:
            print("No speech detected, listening again...")
        except sr.UnknownValueError:
            print("Could not understand audio")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()