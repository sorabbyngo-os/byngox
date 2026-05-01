# Byngox — Unified AI Agent Runtime
# 8 async + 5 sync health intelligence agents
# Build: docker build -t byngox .
# Run:   docker run --network host --env-file .env byngox

FROM python:3.12-slim

LABEL org.opencontainers.image.title="Byngox"
LABEL org.opencontainers.image.description="Sorabbyngo 13-agent health intelligence swarm"
LABEL org.opencontainers.image.vendor="Sorabbyngo Company"
LABEL org.opencontainers.image.source="https://github.com/sorabbyngo-Labs/byngox"

WORKDIR /opt/byngox

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Source
COPY . .

# State directories
RUN mkdir -p /etc/sorabbyngo/byngox
VOLUME ["/etc/sorabbyngo/byngox"]

# Environment defaults
ENV NATS_URL=nats://localhost:4223
ENV OLLAMA_URL=http://localhost:11434
ENV NOVELA_URL=http://localhost:8001
ENV NOVELA_API_URL=http://localhost:8001
ENV LOG_LEVEL=INFO

HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python3 -c "import nats; print('ok')" || exit 1

CMD ["python3", "byngox.py"]
