# Use lightweight Python 3.11 image
FROM python:3.11-slim

# Set environment variables to:
# 1. PYTHONUNBUFFERED: Ensure logs are streamed immediately
# 2. DEBIAN_FRONTEND: Avoid interactive dialogs during package installation
ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory inside the container
WORKDIR /app

# Install system dependencies:
# 1. ffmpeg: Required for audio playback.
# 2. libpq-dev: Required for PostgreSQL driver (psycopg2).
# 3. nodejs: Required by yt-dlp for JavaScript execution (YouTube signature decryption).
# 4. gcc: Required for compiling certain Python packages.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpq-dev \
    nodejs \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary local directories
RUN mkdir -p assets/musicBot/musicTemp \
    && mkdir -p assets/messageHistory

# Startup command
CMD ["python", "DPX_Discord_Bot.py"]
