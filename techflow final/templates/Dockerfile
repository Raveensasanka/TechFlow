FROM python:3.11-slim

WORKDIR /app

# System dependencies (add more as needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Ensure uploads directory exists at container start
RUN mkdir -p static/uploads

# Railway (and most platforms) provide PORT; default to 5000 locally
ENV PORT=5000

EXPOSE 5000

CMD ["python", "run.py"]

