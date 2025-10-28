import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain.tools import tool

load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:latest")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")

@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"

@tool
def get_weather(location: str) -> str:
    """Get weather information for a location."""
    return f"Weather in {location}: Sunny, 72°F"

llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_URL)

def run_agent(user_input: str):
    """Manually route tools or fallback to LLM."""
    if "search" in user_input.lower():
        query = user_input.split("search")[-1].strip()
        result = search.invoke({"query": query})
        return f"🔍 Tool used: search\n\n{result}"
    elif "weather" in user_input.lower():
        location = user_input.split("in")[-1].strip()
        result = get_weather.invoke({"location": location})
        return f"🌤️ Tool used: get_weather\n\n{result}"
    else:
        response = llm.invoke(user_input)
        return response.content
