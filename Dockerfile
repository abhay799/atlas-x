FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy source code
COPY . .

# Expose port
EXPOSE 8000

# Production command
CMD ["sh", "-c", "uvicorn atlas.api.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
