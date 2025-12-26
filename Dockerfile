FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN echo "insecure" > /root/.curlrc && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    rm /root/.curlrc

# Copy project files
COPY pyproject.toml uv.lock* README.md ./
COPY src/ ./src/
COPY app.py ./
COPY .streamlit/ ./.streamlit/

# Install uv
RUN pip install uv

# Install Python dependencies
RUN uv pip install --system -e .

# Expose Streamlit port
EXPOSE 8501

# Expose Ollama port
EXPOSE 11434

# Create startup script
RUN echo '#!/bin/bash\n\
# Start Ollama in the background\n\
ollama serve &\n\
\n\
# Wait for Ollama to be ready\n\
echo "Waiting for Ollama to start..."\n\
sleep 5\n\
\n\
# Pull the default model\n\
echo "Pulling mistral model..."\n\
OLLAMA_HOST=0.0.0.0:11434 ollama pull\n\
\n\
# Start Streamlit\n\
echo "Starting Streamlit..."\n\
streamlit run app.py --server.port=8501 --server.address=0.0.0.0\n\
' > /app/start.sh && chmod +x /app/start.sh

# Run the startup script
CMD ["/app/start.sh"]
