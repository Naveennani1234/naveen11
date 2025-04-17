# Web Scraper with Flask Viewer

This project consists of two main components:
1. Web Scraper - Available in two implementations:
   - A Node.js script that uses Puppeteer to scrape content from a specified URL
   - A Python script that uses built-in libraries to scrape content as a fallback
2. A Python Flask web server that hosts the scraped content as JSON and provides a simple UI

## Project Structure

- `scrape.js` - Node.js script using Puppeteer for web scraping
- `fetch_data.py` - Python-based web scraper (alternative implementation)
- `server.py` - Flask web server to serve the scraped content
- `setup_and_run.sh` - Shell script to run the scraper and server
- `Dockerfile` - Multi-stage Docker build definition (for reference)

## Requirements

### Node.js Requirements
- Node.js v14 or higher
- npm or yarn
- Puppeteer package

```bash
npm install puppeteer
```

### Python Requirements
- Python 3.8 or higher
- Flask

```bash
pip install flask
```

## How to Use

### Option 1: Running with Node.js (Puppeteer)

1. Scrape a website:
```bash
node scrape.js https://example.com
```

2. Start the Flask server:
```bash
python server.py
```

### Option 2: Running with Python Scraper (Fallback)

If Puppeteer has issues with Chrome dependencies, use the Python scraper:

```bash
python fetch_data.py https://example.com
python server.py
```

### Option 3: Using the Combined Script

For convenience, you can use the provided shell script:

```bash
./setup_and_run.sh https://example.com
```

## Accessing the Scraped Data

Once the server is running:

- JSON API: `http://localhost:5000/`
- Simple UI: `http://localhost:5000/ui`

## Docker Implementation (Reference)

This project also includes a Dockerfile that demonstrates how to create a multi-stage build:

1. Stage 1: Node.js with Puppeteer for scraping
2. Stage 2: Python with Flask for serving the content

To build and run the Docker container:

```bash
docker build -t web-scraper .
docker run -p 5000:5000 -e SCRAPE_URL=https://example.com web-scraper
```
