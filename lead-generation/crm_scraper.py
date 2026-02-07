#!/usr/bin/env python3
"""
Job 5: "CRM-Ready" Lead List - Apex Realty Marketing
Transform quotes into CRM lead format, CSV output
"""

import csv
import re
from playwright.sync_api import sync_playwright

def split_name(full_name):
    """Split full name into first and last"""
    parts = full_name.strip().split()
    if len(parts) == 1:
        return parts[0], ""
    elif len(parts) == 2:
        return parts[0], parts[1]
    else:
        # Handle multi-part names (e.g., "J.K. Rowling", "A.A. Milne")
        # Last part is last name, everything else is first name
        return " ".join(parts[:-1]), parts[-1]

def last_name_starts_with_a_to_m(last_name):
    """Check if last name starts with A-M (case insensitive)"""
    if not last_name:
        return False
    first_letter = last_name[0].upper()
    return 'A' <= first_letter <= 'M'

def main():
    leads = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Scraping quotes from quotes.toscrape.com...")
        page.goto("http://quotes.toscrape.com/")
        page.wait_for_load_state("networkidle")
        
        # Get first 10 quotes
        quote_elements = page.query_selector_all("div.quote")[:10]
        print(f"Found {len(quote_elements)} quotes to process")
        
        for i, quote_elem in enumerate(quote_elements):
            # Extract quote text
            text_elem = quote_elem.query_selector("span.text")
            quote_text = text_elem.inner_text() if text_elem else ""
            
            # Extract author
            author_elem = quote_elem.query_selector("small.author")
            author = author_elem.inner_text() if author_elem else "Unknown"
            
            # Split name
            first_name, last_name = split_name(author)
            
            # Check filter: last name must start with A-M
            if not last_name_starts_with_a_to_m(last_name):
                print(f"  {i+1}. {author} - SKIPPED (last name '{last_name}' starts with {last_name[0] if last_name else 'N/A'})")
                continue
            
            # Create lead record
            lead = {
                "First Name": first_name,
                "Last Name": last_name,
                "Lead Status": "New",
                "Notes": quote_text
            }
            leads.append(lead)
            print(f"  {i+1}. {author} -> {first_name} {last_name} - ADDED")
        
        browser.close()
    
    # Save as CSV
    filename = "jobs/The CRM-Ready Lead List/results.csv"
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        if leads:
            writer = csv.DictWriter(f, fieldnames=["First Name", "Last Name", "Lead Status", "Notes"])
            writer.writeheader()
            writer.writerows(leads)
    
    print(f"\nComplete! Processed {len(quote_elements)} quotes, {len(leads)} leads passed filter A-M")
    print(f"Saved to: {filename}")
    
    # Print preview
    print("\n--- CSV PREVIEW (first 3 rows) ---")
    for lead in leads[:3]:
        print(f"{lead['First Name']:<15} {lead['Last Name']:<15} {lead['Lead Status']:<10} {lead['Notes'][:50]}...")
    
    return leads

if __name__ == "__main__":
    main()
