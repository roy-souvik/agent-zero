# from langchain_ollama.chat_models import ChatOllama
# from langchain.tools import tool

# @tool
# def search(query: str) -> str:
#     """Search for information."""
#     return f"Results for: {query}"

# @tool
# def get_weather(location: str) -> str:
#     """Get weather information for a location."""
#     return f"Weather in {location}: Sunny, 72°F"

# llm = ChatOllama(model="llama3", base_url="http://ollama:11434")

# def run_agent(user_input: str):
#     """Simple manual dispatcher."""
#     if "search" in user_input.lower():
#         query = user_input.split("search")[-1].strip()
#         result = search.invoke({"query": query})
#         print(f"Tool used: search\n{result}")
#     elif "weather" in user_input.lower():
#         location = user_input.split("in")[-1].strip()
#         result = get_weather.invoke({"location": location})
#         print(f"Tool used: get_weather\n{result}")
#     else:
#         # fallback to LLM
#         response = llm.invoke(user_input)
#         print(response.content)

# # Test
# run_agent("use the search tool to find AI agents")
# run_agent("use the get_weather tool to check weather in Paris")
# # run_agent("what is 7 + 11?")
# # run_agent("Why do parrots have colorful feathers?")

# # for chunk in llm.stream("Why do parrots have colorful feathers?"):
# #     print(chunk.text, end="|", flush=True)

# for response in llm.batch_as_completed([
#     "Why do parrots have colorful feathers?",
#     "How do airplanes fly?",
#     "What is quantum computing?"
# ]):
#     print(response)

import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain.tools import tool
from langchain.agents import create_agent
# from langchain_ollama.chat_models import ChatOllama

# Load environment variables
load_dotenv()

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
CHROMA_URL = os.getenv("CHROMA_URL", "http://chroma:8000")
CHROMA_PATH = os.getenv("CHROMA_PATH", "/workspace/db")
# CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION", "agent_memory")

# Setup LLM
llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_URL)

embeddings = OllamaEmbeddings(model=OLLAMA_MODEL, base_url=OLLAMA_URL)

# Setup Chroma
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embeddings)

@tool
def add_doc(text: str):
    """Add text to Chroma vector store."""
    db.add_texts([text])
    return "Document added."

@tool
def search_doc(query: str):
    """Search Chroma for relevant info."""
    results = db.similarity_search(query, k=2)
    return "\n".join([r.page_content for r in results]) or "No matches found."

agent = create_agent(llm, tools=[add_doc, search_doc])
