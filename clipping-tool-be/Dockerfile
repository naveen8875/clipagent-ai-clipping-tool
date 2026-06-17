# Multi-stage Dockerfile
# Stage 1: frontend build
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend dependency files
COPY frontend/package*.json ./

# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source
COPY frontend/ ./

# Build the frontend app
RUN npm run build

# Stage 2: backend runtime
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY app/ ./app/
COPY prompts/ ./prompts/
COPY .env.example ./

# Copy the built frontend output
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create required runtime directories
RUN mkdir -p output/clips output/collections output/metadata uploads data temp

# Copy default configuration
COPY data/settings.example.json ./data/settings.json

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
