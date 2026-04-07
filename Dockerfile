# ── Email Triage OpenEnv — Dockerfile ────────────────────────────────────────
# Builds a containerised FastAPI server that exposes the OpenEnv HTTP endpoints.
# Designed to run on 2 vCPU / 8 GB RAM as per hackathon infra constraints.

FROM python:3.11-slim

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY models.py .
COPY openenv.yaml .
COPY server/ ./server/

# Health check — OpenEnv validator pings /health
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
