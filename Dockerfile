FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p project/models project/datasets project/logs project/runs

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV AUTOML_HOST=0.0.0.0
ENV AUTOML_PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "project.api_server:app", "--host", "0.0.0.0", "--port", "8000"]