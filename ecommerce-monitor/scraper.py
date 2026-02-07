#!/usr/bin/env python3
"""
Job 4: Competitor Book Prices - Travel Category
Data transformation: currency stripping, rating conversion, boolean conversion
"""

from playwright.sync_api import sync_playwright
import json
import time
import re

print('[Job 4] Starting: Competitor Book Prices - Travel Category')
print('[Job 4] Target: books.toscrape.com/catalogue/category/books/travel_2/')
print('[Job 4] Transformations: GBP to float, text to int, text to bool')
print()

# Star rating text to integer mapping
STAR_MAP = {
    'One': 1,
    'Two': 2,
    'Three': 3,
    'Four': 4,
    'Five': 5
}

start_time = time.time()

with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp('http://localhost:9222')
    page = browser.contexts[0].pages[0]
    
    # Navigate to Travel category
    url = 'http://books.toscrape.com/catalogue/category/books/travel_2/index.html'
    print(f'[Scraper] Navigating to: {url}')
    page.goto(url)
    page.wait_for_timeout(2000)
    
    # Extract all books with transformations applied in JavaScript
    print('[Scraper] Extracting and transforming book data...')
    books = page.evaluate("""
        () => {
            const books = [];
            const articles = document.querySelectorAll('article.product_pod');
            
            articles.forEach(article => {
                // Title
                const title = article.querySelector('h3 a').getAttribute('title');
                
                // Price: strip £ symbol and convert to float
                const priceText = article.querySelector('.price_color').innerText;
                const price = parseFloat(priceText.replace('£', '').trim());
                
                // Star rating: convert class text to integer
                const starClass = article.querySelector('.star-rating').className;
                const starMatch = starClass.match(/star-rating (\\w+)/);
                const starText = starMatch ? starMatch[1] : 'Zero';
                
                // Map text to number
                const starMap = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5};
                const star_rating = starMap[starText] || 0;
                
                // Availability: convert to boolean
                const availText = article.querySelector('.availability').innerText.trim();
                const is_in_stock = availText.includes('In stock');
                
                books.push({
                    title: title,
                    price: price,
                    star_rating: star_rating,
                    is_in_stock: is_in_stock
                });
            });
            
            return books;
        }
    """)
    
    browser.close()

elapsed = time.time() - start_time

print(f'[Scraper] Found {len(books)} books')
print()

# Validate data types
print('[Validation] Checking data types...')
all_valid = True
for i, book in enumerate(books, 1):
    checks = [
        (isinstance(book['price'], float) or isinstance(book['price'], int), f'price is number'),
        (isinstance(book['star_rating'], int), f'star_rating is integer'),
        (isinstance(book['is_in_stock'], bool), f'is_in_stock is boolean')
    ]
    for passed, check_name in checks:
        if not passed:
            print(f'  [X] Book {i}: {check_name} FAILED')
            all_valid = False

if all_valid:
    print('  [OK] All data types correct!')

print()
print('='*60)
print(f'[Job 4] COMPLETE!')
print(f'[Job 4] Books extracted: {len(books)}')
print(f'[Job 4] Time: {elapsed:.2f}s')
print('='*60)

# Save to Complete Work folder
output_path = '../Complete Work/travel_books.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(books, f, indent=2, ensure_ascii=False)

print()
print(f'[Job 4] Results saved to: {output_path}')
print()
print('Sample output:')
print(json.dumps(books[0], indent=2) if books else 'No books found')
