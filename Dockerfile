FROM python:3.12-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy everything needed for the build
COPY pyproject.toml README.md ./
COPY src/ src/

# Install the package and its dependencies
RUN pip install --no-cache-dir .

# Copy runtime assets
COPY templates/ templates/
COPY static/ static/

# Create a non-root user and writable data directory
RUN useradd --create-home librarian && \
    mkdir -p /app/data && \
    chown -R librarian:librarian /app/data

USER librarian

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/reading-room/health')"]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
