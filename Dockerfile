FROM ghcr.io/astral-sh/uv:0.13.5 AS uv
FROM python:3.14.9-slim AS base

# Prevent stale .pyc bytecode and ensure real-time log output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OVERDUE_DATABASE_URL=sqlite+aiosqlite:////app/data/overdue.db \
    PATH="/app/.venv/bin:$PATH" \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app
COPY --from=uv /uv /usr/local/bin/uv

# Copy everything needed for the build
COPY pyproject.toml uv.lock README.md ./
COPY src/ src/

# Editable install so Python reads from /app/src directly.
# This is critical for Compose Watch: synced file changes take
# effect immediately instead of being shadowed by site-packages.
RUN uv sync --locked --no-dev --no-cache && \
    /usr/local/bin/python -m pip uninstall --yes pip

# Copy runtime assets
COPY templates/ templates/
COPY static/ static/

# Create a non-root user and writable data directory
RUN useradd --create-home librarian && \
    mkdir -p /app/data && \
    chown -R librarian:librarian /app/data /app/src /app/templates /app/static

USER librarian

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/reading-room/health')"]

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
