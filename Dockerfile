# =============================================================================
# AQUA NEON (Team AutoNex) — Production Dockerfile
# Multi-Service Container: FastAPI (Port 8000) + Streamlit (Port 8501 / Dynamic PORT)
# =============================================================================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive \
    PORT=8501

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy complete project code & assets
COPY . .

# Ensure data directory exists and set permissions
RUN mkdir -p /app/data && chmod +x /app/start_platform.sh

# Expose ports for FastAPI (8000) and Streamlit (8501)
EXPOSE 8000 8501

# Healthcheck targeting FastAPI microservice
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start services via unified launch script
CMD ["/bin/bash", "./start_platform.sh"]
