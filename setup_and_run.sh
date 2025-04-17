#!/bin/bash

# Print execution steps
set -x

# Install Python Flask (if not already installed)
pip install flask

# Try to scrape with Node.js/Puppeteer first
echo "Attempting to scrape with Puppeteer..."
URL=${1:-"https://example.com"}
node scrape.js $URL || {
  echo "Puppeteer scraping failed, falling back to Python scraper..."
  python fetch_data.py $URL
}

# Start the Flask server
echo "Starting Flask server..."
python server.py