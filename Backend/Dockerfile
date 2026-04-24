FROM python:3.12-slim

WORKDIR /app

# Minimal system deps — opencv-python-headless bundles its own GL libs
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Persistent data directories
RUN mkdir -p data/uploads data/reports

# Railway injects $PORT at runtime; default 8000 for local docker run
ENV PORT=8000

EXPOSE $PORT

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
