# Multi-stage build for efficient production image
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Production stage
FROM python:3.12-slim AS production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy uv from builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Create non-root user
RUN groupadd -r wanikani && useradd -r -g wanikani wanikani

# Set working directory and ownership
WORKDIR /app
RUN chown wanikani:wanikani /app

# Copy virtual environment from builder
COPY --from=builder --chown=wanikani:wanikani /app/.venv /app/.venv

# Copy application code
COPY --chown=wanikani:wanikani . .

# Install the project
RUN uv sync --frozen --no-dev

# Switch to non-root user
USER wanikani

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Default command (can be overridden)
CMD ["python", "-m", "wanikani_mcp.server", "--mode", "http", "--host", "0.0.0.0", "--port", "8000"]