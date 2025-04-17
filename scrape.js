/**
 * Web Scraper using Puppeteer
 * 
 * This script uses Puppeteer to scrape content from a specified URL.
 * Usage: node scrape.js [URL]
 * 
 * The URL can also be specified via the SCRAPE_URL environment variable.
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

// Get the URL to scrape from command line arguments or environment variable
const urlToScrape = process.argv[2] || process.env.SCRAPE_URL;

if (!urlToScrape) {
  console.error('Error: No URL specified');
  console.error('Usage: node scrape.js [URL]');
  console.error('Or set the SCRAPE_URL environment variable');
  process.exit(1);
}

async function scrapeWebsite(url) {
  console.log(`Starting to scrape: ${url}`);
  
  // Launch the browser with appropriate flags for running in a container
  const browser = await puppeteer.launch({
    headless: 'new', // Use the new headless mode
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-accelerated-2d-canvas',
      '--disable-gpu'
    ]
  });

  try {
    const page = await browser.newPage();
    
    // Set viewport to a reasonable size
    await page.setViewport({ width: 1280, height: 800 });
    
    // Enable request interception for better performance
    await page.setRequestInterception(true);
    
    // Skip loading images, fonts, and stylesheets for faster scraping
    page.on('request', (req) => {
      const resourceType = req.resourceType();
      if (['image', 'font', 'stylesheet'].includes(resourceType)) {
        req.abort();
      } else {
        req.continue();
      }
    });
    
    // Navigation timeout increased for slower websites
    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 60000 });
    
    console.log('Page loaded, extracting data...');
    
    // Extract data from the page
    const data = await page.evaluate(() => {
      return {
        title: document.title,
        url: window.location.href,
        heading: document.querySelector('h1') ? document.querySelector('h1').innerText : null,
        metaDescription: document.querySelector('meta[name="description"]') 
          ? document.querySelector('meta[name="description"]').getAttribute('content') 
          : null,
        links: Array.from(document.querySelectorAll('a')).slice(0, 20).map(link => ({
          text: link.innerText.trim(),
          href: link.href
        })),
        paragraphs: Array.from(document.querySelectorAll('p')).slice(0, 10).map(p => p.innerText.trim()),
        timestamp: new Date().toISOString()
      };
    });
    
    console.log('Data extracted successfully');
    
    // Save the scraped data to a JSON file
    const scrapedData = {
      source_url: url,
      scraped_at: new Date().toISOString(),
      data: data
    };
    
    // Write data to file
    fs.writeFileSync(
      path.join(__dirname, 'scraped_data.json'),
      JSON.stringify(scrapedData, null, 2),
      'utf8'
    );
    
    console.log('Data saved to scraped_data.json');
    
    return scrapedData;
  } catch (error) {
    console.error('Error during scraping:', error);
    
    // Save error information to the JSON file
    const errorData = {
      source_url: url,
      scraped_at: new Date().toISOString(),
      error: {
        message: error.message,
        stack: error.stack
      }
    };
    
    fs.writeFileSync(
      path.join(__dirname, 'scraped_data.json'),
      JSON.stringify(errorData, null, 2),
      'utf8'
    );
    
    console.error('Error data saved to scraped_data.json');
    throw error;
  } finally {
    await browser.close();
    console.log('Browser closed');
  }
}

// Execute the scraping
scrapeWebsite(urlToScrape)
  .then(() => {
    console.log('Scraping completed successfully');
    process.exit(0);
  })
  .catch(error => {
    console.error('Scraping failed:', error);
    process.exit(1);
  });
