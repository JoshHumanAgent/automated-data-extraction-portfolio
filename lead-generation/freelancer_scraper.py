#!/usr/bin/env python3
"""
Freelancer.com Raid v2 - Shorter timeout, faster extraction
"""

import re
from playwright.sync_api import sync_playwright

def extract_price_value(price_text):
    """Extract numeric value from price string"""
    numbers = re.findall(r'\$([\d,]+)', price_text)
    if numbers:
        return int(numbers[-1].replace(',', ''))
    return 0

def main():
    jobs = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Freelancer Raid v2: Loading...")
        
        # Go to site with shorter timeout
        try:
            page.goto("https://www.freelancer.com/jobs/web-scraping/", timeout=15000)
            page.wait_for_load_state("domcontentloaded", timeout=10000)
        except:
            print("Timeout - checking if page loaded anyway...")
        
        # Wait extra moment for JS
        import time
        time.sleep(3)
        
        # Get body text to check if we're blocked
        body_text = page.inner_text("body")[:500]
        print(f"Page loaded: {body_text[:200]}...")
        
        # Try multiple selectors
        project_cards = []
        selectors = ["[data-project-id]", ".JobSearchCard-item", ".project-item", ".JobCard", ".fl-tile"]
        
        for selector in selectors:
            try:
                cards = page.query_selector_all(selector)
                if cards:
                    project_cards = cards
                    print(f"Found {len(cards)} cards with: {selector}")
                    break
            except:
                pass
        
        if not project_cards:
            print("No cards found - trying to find any clickable project elements...")
            # Try just finding all links with /projects/ in href
            links = page.query_selector_all('a[href*="/projects/"]')
            print(f"Found {len(links)} project links")
            
        # Parse up to 30 projects
        for i, card in enumerate(project_cards[:30]):
            try:
                # Get inner text and parse
                text = card.inner_text()
                
                # Title - usually prominent text
                title_match = re.search(r'^([^\n\r]+)', text)
                title = title_match.group(1).strip()[:60] if title_match else "Unknown"
                
                # Price - look for $X or $X - $Y pattern
                price_match = re.search(r'\$[\d,]+(?:\s+-\s+\$[\d,]+)?', text)
                price = price_match.group(0) if price_match else ""
                
                # Time - look for time patterns
                time_match = re.search(r'(\d+\s+(?:minute|hour|day|week)[s]?|ending\s+\w+)', text, re.I)
                time_text = time_match.group(0) if time_match else "Unknown"
                
                # Link
                link_elem = card.query_selector("a")
                href = link_elem.get_attribute("href") if link_elem else ""
                url = f"https://www.freelancer.com{href}" if href.startswith("/") else href
                
                # Filter
                price_val = extract_price_value(price)
                if price_val < 50:
                    continue
                    
                jobs.append({
                    'title': title,
                    'price': price if price else f"${price_val}",
                    'time': time_text,
                    'url': url,
                    'recency': price_val  # Sort lower price first (usually newer/simpler projects)
                })
                
                print(f"  [{len(jobs)}] {title[:40]:<40} | {price}")
                
            except Exception as e:
                pass
        
        browser.close()
    
    # Sort and display
    jobs.sort(key=lambda x: x['recency'], reverse=True)
    
    print(f"\n{'='*70}")
    print(f"COMPLETE: {len(jobs)} qualified leads (>=$50)")
    
    # Save
    import csv
    import os
    os.makedirs("jobs/Freelancer_Raid", exist_ok=True)
    
    with open("jobs/Freelancer_Raid/v2_leads.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Price", "Time Left", "Link"])
        for job in jobs:
            writer.writerow([job['title'], job['price'], job['time'], job['url']])
    
    # Markdown
    if jobs:
        print("\n| Title | Price | Time | Link |")
        print("| :--- | :--- | :--- | :--- |")
        for job in jobs[:10]:
            title = job['title'][:35] + "..." if len(job['title']) > 35 else job['title']
            print(f"| {title} | {job['price']} | {job['time']} | [Bid]({job['url']}) |")
    
    return jobs

if __name__ == "__main__":
    main()
