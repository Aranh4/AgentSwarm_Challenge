# ============================================================================
# CloudWalk Agent Swarm - Production Dockerfile
# ============================================================================
# Base: Python 3.11-slim for minimal footprint
# Purpose: Containerized FastAPI + CrewAI agent swarm application
# ============================================================================

# Use official Python runtime as parent image
FROM python:3.11-slim

# Set environment variables for Python optimization
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set working directory
WORKDIR /app

# Install system dependencies required for Python packages
# - build-essential: Required for compiling some Python dependencies
# - curl: Useful for health checks and debugging
# Clean up apt cache to minimize image size
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
# Separate layer for better Docker cache utilization
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for ChromaDB persistence
# Ensures vector store data is accessible for volume mounting
RUN mkdir -p data/chromadb data/database

# Expose port for FastAPI application
EXPOSE 8080

# Health check for container orchestration
# Verifies app is responding on /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run application using uvicorn ASGI server
# --host 0.0.0.0: Accept connections from outside container
# --port 8080: Standard FastAPI port
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
