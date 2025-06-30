FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app /app
COPY ./app/static /app/static

# Create output directory and set permissions
RUN mkdir -p /app/output && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port (Railway will set PORT environment variable)
EXPOSE 8000

# Health check using curl (built into Python image) or simple command
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:$PORT/health')" || exit 1

# Use Railway's PORT environment variable or default to 8000
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]

