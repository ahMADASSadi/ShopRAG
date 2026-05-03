FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

# Install system dependencies required by psycopg2 / sentence-transformers
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project manifest and lock file first for layer caching
COPY pyproject.toml uv.lock* ./

# Install only production dependencies from the lock file
RUN uv sync --frozen --no-dev --no-cache

# Pre-download the embedding model so the container starts instantly
RUN uv run python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application code
COPY app/ ./app/

# Create logs directory
RUN mkdir -p logs

# Create non-root user
RUN useradd -m -u 1000 shoprag && chown -R shoprag:shoprag /app
USER shoprag

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
