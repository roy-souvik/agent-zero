FROM python:3.12-slim

WORKDIR /workspace

# Add audio dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    curl \
    portaudio19-dev \
    python3-pyaudio \
    espeak \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]