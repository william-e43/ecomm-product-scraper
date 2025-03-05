import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random

# Load URLs from CSV
try:
    df = pd.read_csv('sample-product-urls.csv')
except Exception as e:
    print(f"Error loading file: {e}")
    exit()

# Initialize columns
df['title'] = ''
df['price'] = ''
df['description'] = ''
df['rating'] = ''

def scrape_product(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': 'https://www.amazon.com/',
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Title
        title = soup.select_one('#productTitle')
        title = title.text.strip() if title else 'Unknown Product'

        # Multiple price selectors (trying various possibilities)
        price_selectors = [
            '.a-price > span.a-offscreen',           # Standard price
            '#priceblock_ourprice',                  # Older format
            '.priceToPay span.a-offscreen',          # Newer format
            '#corePrice_feature_div .a-price',       # Featured price
            '.apexPriceToPay span.a-offscreen',     # Another variation
        ]
        price = None
        for selector in price_selectors:
            price_elem = soup.select_one(selector)
            if price_elem:
                price = price_elem.text.strip()
                break
        price = price if price else '$0.00'

        # Description
        description = soup.select_one('#productDescription') or soup.select_one('#feature-bullets')
        description = description.text.strip() if description else 'No description'

        # Rating
        rating = soup.select_one('span[data-hook="rating-out-of-text"]') or soup.select_one('.a-icon-alt')
        rating = rating.text.strip() if rating else 'No rating'

        # Debug output
        print(f"URL: {url}")
        print(f"Title: {title}")
        print(f"Price: {price}")
        print(f"Description preview: {description[:100]}...")
        print(f"Rating: {rating}")
        print("---")

        time.sleep(random.uniform(2, 5))
        return title, price, description, rating
    except requests.RequestException as e:
        print(f"Request failed for {url}: {e}")
        return 'Error', '$0.00', 'Error', 'No rating'

# Process each URL
for i, row in df.iterrows():
    try:
        title, price, description, rating = scrape_product(row['url'])
        df.loc[i, 'title'] = title
        df.loc[i, 'price'] = price
        df.loc[i, 'description'] = description
        df.loc[i, 'rating'] = rating
    except Exception as e:
        print(f"Error processing row {i}: {e}")

# Save results
df.to_csv('ecommerce_market_data.csv', index=False)
print("Scraping complete—check ecommerce_market_data.csv!")