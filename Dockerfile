# Stage 1: Build TSX Frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend Runtime
FROM python:3.10-slim

# Install system dependencies for WeasyPrint and Playwright
RUN apt-get update && apt-get install -y \
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
ENV PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT=120000
RUN playwright install --with-deps firefox

COPY . .
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Run DB Migrations then start server
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.main:app --host 0.0.0.0 --port 8001"]
