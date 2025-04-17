"""
Flask Web Server for Scraped Content

This script runs a Flask web server that serves the content scraped by the Node.js script.
The server reads the scraped_data.json file and serves it as JSON when accessed.
"""

import os
import json
import logging
from datetime import datetime
from flask import Flask, jsonify, render_template_string

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Path to the scraped data file
SCRAPED_DATA_FILE = os.path.join(os.path.dirname(__file__), 'scraped_data.json')

def get_scraped_data():
    """
    Read the scraped data from the JSON file.
    Returns the data as a dictionary or an error message if the file doesn't exist.
    """
    try:
        if not os.path.exists(SCRAPED_DATA_FILE):
            logger.warning(f"Scraped data file not found: {SCRAPED_DATA_FILE}")
            return {
                "error": "No scraped data available",
                "message": "Run the scraper first using 'node scrape.js [URL]'",
                "timestamp": datetime.now().isoformat()
            }
        
        with open(SCRAPED_DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from scraped data file: {e}")
        return {
            "error": "Invalid scraped data",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Unexpected error reading scraped data: {e}")
        return {
            "error": "Failed to read scraped data",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.route('/')
def index():
    """
    Serve the scraped data as JSON.
    """
    data = get_scraped_data()
    return jsonify(data)

@app.route('/ui')
def ui():
    """
    Provide a simple HTML UI to display the scraped data.
    """
    data = get_scraped_data()
    
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Scraped Data Viewer</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                color: #333;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 2px solid #eee;
                padding-bottom: 10px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
            }
            .info-box {
                background-color: #f8f9fa;
                border-left: 4px solid #17a2b8;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 0 4px 4px 0;
            }
            .error-box {
                background-color: #fff3f3;
                border-left: 4px solid #dc3545;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 0 4px 4px 0;
            }
            pre {
                background: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                overflow-x: auto;
            }
            code {
                font-family: 'Courier New', Courier, monospace;
            }
            .btn {
                background: #3498db;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 4px;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
                margin-top: 20px;
            }
            .btn:hover {
                background: #2980b9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Scraped Data Viewer</h1>
            
            {% if data.get('error') %}
                <div class="error-box">
                    <h3>Error: {{ data.get('error') }}</h3>
                    <p>{{ data.get('message') }}</p>
                    <p>Timestamp: {{ data.get('timestamp') }}</p>
                </div>
            {% else %}
                <div class="info-box">
                    <p><strong>Source URL:</strong> {{ data.get('source_url') }}</p>
                    <p><strong>Scraped at:</strong> {{ data.get('scraped_at') }}</p>
                </div>
                
                {% if data.get('data') %}
                    <h2>Page Information</h2>
                    <p><strong>Title:</strong> {{ data['data'].get('title') }}</p>
                    <p><strong>URL:</strong> {{ data['data'].get('url') }}</p>
                    
                    {% if data['data'].get('heading') %}
                        <p><strong>Main Heading:</strong> {{ data['data'].get('heading') }}</p>
                    {% endif %}
                    
                    {% if data['data'].get('metaDescription') %}
                        <p><strong>Meta Description:</strong> {{ data['data'].get('metaDescription') }}</p>
                    {% endif %}
                    
                    {% if data['data'].get('paragraphs') %}
                        <h2>Paragraphs</h2>
                        <ul>
                            {% for paragraph in data['data'].get('paragraphs', []) %}
                                <li>{{ paragraph }}</li>
                            {% endfor %}
                        </ul>
                    {% endif %}
                    
                    {% if data['data'].get('links') %}
                        <h2>Links</h2>
                        <ul>
                            {% for link in data['data'].get('links', []) %}
                                <li>
                                    <a href="{{ link.get('href') }}" target="_blank">
                                        {{ link.get('text') or link.get('href') }}
                                    </a>
                                </li>
                            {% endfor %}
                        </ul>
                    {% endif %}
                {% endif %}
            {% endif %}
            
            <h2>Raw JSON Data</h2>
            <pre><code>{{ raw_json }}</code></pre>
            
            <a href="/" class="btn">View Raw JSON</a>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(
        html, 
        data=data, 
        raw_json=json.dumps(data, indent=2)
    )

if __name__ == '__main__':
    # Check if the data file exists and log a warning if it doesn't
    if not os.path.exists(SCRAPED_DATA_FILE):
        logger.warning(
            f"Scraped data file not found: {SCRAPED_DATA_FILE}. "
            "Run the scraper first using 'node scrape.js [URL]'"
        )
    
    # Run the Flask app
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
