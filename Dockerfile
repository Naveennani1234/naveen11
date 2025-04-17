# Multi-stage Docker build for a web scraper with Python Flask viewer

# Stage 1: Scraper Stage (Node.js with Puppeteer)
FROM node:18-slim AS scraper

# Set working directory
WORKDIR /app

# Install dependencies for Puppeteer/Chromium
RUN apt-get update && apt-get install -y \
    glib-2.0 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libfontconfig1 \
    fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

# Skip Puppeteer's Chromium download since we'll use the system version
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true

# Copy package.json and install dependencies
COPY package.json ./
RUN npm install

# Copy the scraper script
COPY scrape.js ./

# Create a directory for the scraped data
RUN mkdir -p /app/data

# Default URL to scrape if not specified
ENV SCRAPE_URL=https://example.com

# Run the scraper
RUN node scrape.js ${SCRAPE_URL} || echo "Scraping failed, will try again at runtime"

# Stage 2: Python Flask Server (Final Stage)
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install Flask
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the server script
COPY server.py ./
COPY fetch_data.py ./

# Copy the scraped data from the previous stage
COPY --from=scraper /app/scraped_data.json ./scraped_data.json || true

# Expose port 5000 for the Flask app
EXPOSE 5000

# Create an entrypoint script that tries Puppeteer first, falls back to Python scraper
COPY setup_and_run.sh ./
RUN chmod +x setup_and_run.sh

# Set environment variable for URL
ENV SCRAPE_URL=https://example.com

# Run the entrypoint script
ENTRYPOINT ["./setup_and_run.sh"]