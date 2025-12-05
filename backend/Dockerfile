FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU version first (lighter and prevents memory spikes)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install sentence-transformers separately
RUN pip install --no-cache-dir sentence-transformers==2.3.1

# Copy production requirements
COPY backend/requirements-prod.txt .

# Install remaining Python dependencies
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY backend/ .

# Create necessary directories
RUN mkdir -p /app/data/faiss_index

# Expose port
ENV PORT=8080
EXPOSE $PORT

# Run the application
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
