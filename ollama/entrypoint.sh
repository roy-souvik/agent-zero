#!/bin/sh
set -e

# Start Ollama server in the background
ollama serve &

# Wait for the server to be ready
until curl -s http://localhost:11434/; do
  echo "Waiting for Ollama server..."
  sleep 1
done

# Pull the model
# ollama pull llama3.1
# ollama pull qwen3:1.7b
ollama pull deepseek-r1:latest

# Wait for background server to exit (keep container running)
wait