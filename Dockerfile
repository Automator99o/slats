FROM python:3.11-slim

# System deps: FFmpeg + Chromium dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2 \
    libxshmfence1 fonts-liberation fonts-noto-color-emoji \
    && rm -rf /var/lib/apt/lists/*

# Python deps
RUN pip install --no-cache-dir playwright

# Install Chromium for Playwright
RUN playwright install chromium

WORKDIR /app

# Copy project files
COPY animation.html engine.py batch.csv ./

# Create output directory
RUN mkdir -p /app/output /tmp/frames

# Volume mounts
VOLUME ["/app/output", "/app/batch.csv"]

ENTRYPOINT ["python", "engine.py"]
CMD ["--batch", "batch.csv", "--output", "/app/output"]
