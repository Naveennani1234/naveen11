"""
Simple URL Fetcher

This script uses Python's built-in libraries to fetch content from a specified URL.
It's a fallback for when Puppeteer can't be used due to environment limitations.
"""

import os
import json
import sys
import logging
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
import re
from html.parser import HTMLParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleHTMLParser(HTMLParser):
    """A simple HTML parser that extracts basic elements from a webpage."""
    
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.headings = []
        self.in_heading = False
        self.current_heading = ""
        self.links = []
        self.paragraphs = []
        self.in_paragraph = False
        self.current_paragraph = ""
        self.meta_description = None
    
    def handle_starttag(self, tag, attrs):
        if tag == 'title':
            self.in_title = True
        elif tag.startswith('h') and len(tag) == 2 and tag[1].isdigit():
            self.in_heading = True
            self.current_heading = ""
        elif tag == 'a':
            href = next((attr[1] for attr in attrs if attr[0] == 'href'), None)
            if href:
                self.links.append({
                    'text': '',
                    'href': href
                })
        elif tag == 'p':
            self.in_paragraph = True
            self.current_paragraph = ""
        elif tag == 'meta':
            # Initialize variables
            is_description = False
            content = None
            
            # Process attributes
            for attr in attrs:
                name, value = attr
                
                # Check for name attribute with description value
                if name == 'name' and value is not None:
                    if value.lower() == 'description':
                        is_description = True
                        
                # Capture the content value
                elif name == 'content':
                    content = value
            
            # If this is a meta description tag and it has content, store it
            if is_description and content:
                self.meta_description = content
    
    def handle_endtag(self, tag):
        if tag == 'title':
            self.in_title = False
        elif tag.startswith('h') and len(tag) == 2 and tag[1].isdigit():
            self.in_heading = False
            if self.current_heading.strip():
                self.headings.append(self.current_heading.strip())
        elif tag == 'p':
            self.in_paragraph = False
            if self.current_paragraph.strip():
                self.paragraphs.append(self.current_paragraph.strip())
    
    def handle_data(self, data):
        if self.in_title:
            self.title += data
        elif self.in_heading:
            self.current_heading += data
        elif self.in_paragraph:
            self.current_paragraph += data
        
        # Add text to the most recent link if we're inside a link tag
        if self.links and 'text' in self.links[-1] and not self.links[-1]['text']:
            self.links[-1]['text'] = data.strip()

def scrape_website(url):
    """
    Fetch and parse a website using Python's built-in libraries.
    Returns a dictionary with the scraped data.
    """
    logger.info(f"Starting to fetch: {url}")
    
    try:
        # Create a request with a user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        req = Request(url, headers=headers)
        
        # Open the URL and read the content
        with urlopen(req, timeout=30) as response:
            html_content = response.read().decode('utf-8')
        
        logger.info("Page fetched successfully, parsing content...")
        
        # Parse the HTML content
        parser = SimpleHTMLParser()
        parser.feed(html_content)
        
        # Prepare the data dictionary
        data = {
            'title': parser.title,
            'url': url,
            'heading': parser.headings[0] if parser.headings else None,
            'metaDescription': parser.meta_description,
            'links': parser.links[:20],  # Limit to 20 links
            'paragraphs': parser.paragraphs[:10],  # Limit to 10 paragraphs
            'timestamp': datetime.now().isoformat()
        }
        
        # Create the final data structure
        scraped_data = {
            'source_url': url,
            'scraped_at': datetime.now().isoformat(),
            'data': data
        }
        
        # Save the data to a JSON file
        with open('scraped_data.json', 'w', encoding='utf-8') as f:
            json.dump(scraped_data, f, indent=2)
        
        logger.info("Data saved to scraped_data.json")
        return scraped_data
        
    except (URLError, HTTPError) as e:
        logger.error(f"Error fetching URL: {e}")
        error_data = {
            'source_url': url,
            'scraped_at': datetime.now().isoformat(),
            'error': {
                'message': str(e),
                'type': type(e).__name__
            }
        }
        
        with open('scraped_data.json', 'w', encoding='utf-8') as f:
            json.dump(error_data, f, indent=2)
        
        logger.error("Error data saved to scraped_data.json")
        return error_data
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        error_data = {
            'source_url': url,
            'scraped_at': datetime.now().isoformat(),
            'error': {
                'message': str(e),
                'type': type(e).__name__
            }
        }
        
        with open('scraped_data.json', 'w', encoding='utf-8') as f:
            json.dump(error_data, f, indent=2)
        
        logger.error("Error data saved to scraped_data.json")
        return error_data

if __name__ == "__main__":
    # Get the URL from command line argument or environment variable
    url_to_scrape = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('SCRAPE_URL')
    
    if not url_to_scrape:
        logger.error("No URL specified. Use python fetch_data.py [URL] or set the SCRAPE_URL environment variable.")
        sys.exit(1)
    
    # Execute the scraping
    try:
        scrape_website(url_to_scrape)
        logger.info("Fetching completed successfully")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fetching failed: {e}")
        sys.exit(1)