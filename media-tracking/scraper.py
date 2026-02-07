#!/usr/bin/env python3
"""
IMDB Top 250 Movies - Client: Data_Dave
Requirement: Top 20, CSV format: Rank, Title, Year, Rating
Budget: $127 (if delivered in 10 minutes)
"""

import csv
import re
from playwright.sync_api import sync_playwright

def main():
    movies = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # Use proper User-Agent to avoid 403
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        
        page = context.new_page()
        
        print("IMDB Mission: Loading Top 250...")
        page.goto("https://www.imdb.com/chart/top/")
        page.wait_for_load_state("networkidle")
        
        # Wait for movie list to load
        page.wait_for_selector("li.ipc-metadata-list-summary-item", timeout=15000)
        
        # Get all movie rows
        movie_rows = page.query_selector_all("li.ipc-metadata-list-summary-item")[:20]
        print(f"Found {len(movie_rows)} movies")
        
        for i, row in enumerate(movie_rows, 1):
            try:
                # Get title
                title_elem = row.query_selector("h3.ipc-title__text")
                full_title = title_elem.inner_text() if title_elem else "N/A"
                
                # Parse title: format is "1. The Shawshank Redemption"
                # Remove rank number
                title_clean = re.sub(r'^\d+\.\s*', '', full_title)
                
                # Get year - look for the year span
                year_elem = row.query_selector("span.cli-title-metadata-item")
                year = year_elem.inner_text() if year_elem else "N/A"
                
                # Get rating - look for rating span
                rating_elem = row.query_selector("span.ipc-rating-star--rating") or row.query_selector("[data-testid='ratingGroup'] span")
                if rating_elem:
                    rating = rating_elem.inner_text()
                else:
                    # Try alternative selectors
                    rating_elem = row.query_selector(".ipc-rating-star")
                    rating = rating_elem.inner_text()[:3] if rating_elem else "N/A"
                
                movies.append({
                    'Rank': i,
                    'Title': title_clean,
                    'Year': year,
                    'Rating': rating
                })
                
                print(f"  #{i}: {title_clean[:40]:<40} | {year} | {rating}")
                
            except Exception as e:
                print(f"  Error on movie {i}: {e}")
        
        browser.close()
    
    # Save to CSV
    import os
    os.makedirs("jobs/IMDB_Top250", exist_ok=True)
    
    filename = "jobs/IMDB_Top250/top_20_movies.csv"
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Rank", "Title", "Year", "Rating"])
        writer.writeheader()
        writer.writerows(movies)
    
    print(f"\n{'='*70}")
    print(f"🎬 DELIVERABLE READY FOR DATA_DAVE")
    print(f"Movies scraped: {len(movies)}")
    print(f"Saved to: {filename}")
    print(f"Budget: $127 (pending approval)")
    
    print("\n--- Preview ---")
    print("| Rank | Title | Year | Rating |")
    print("| :--- | :--- | :--- | :--- |")
    for m in movies[:10]:
        title = m['Title'][:35] + "..." if len(m['Title']) > 35 else m['Title']
        print(f"| {m['Rank']} | {title} | {m['Year']} | {m['Rating']} |")
    
    return movies

if __name__ == "__main__":
    main()
