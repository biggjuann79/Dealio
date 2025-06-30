import os
import requests
import random
from bs4 import BeautifulSoup
from postgres_db import save_listing, init_db

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

CITIES = [
    "newyork", "losangeles", "chicago", "houston", "phoenix",
    "philadelphia", "sanantonio", "sandiego", "dallas"
]

def scrape_search_page(city):
    try:
        url = f"https://{city}.craigslist.org/search/sss"
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Skipping {city}: {e}")
        return None

def parse_and_save(city, html):
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select(".result-info")

    for item in items:
        try:
            title_tag = item.select_one(".result-title")
            title = title_tag.text
            url = title_tag["href"]
            post_id = item.parent.get("data-pid", "nopid")
            price_tag = item.select_one(".result-price")
            price = float(price_tag.text.replace("$", "")) if price_tag else 0.0

            listing = {
                "id": f"{city}_{post_id}",
                "title": title,
                "price": price,
                "category": "general",
                "deal_score": round(random.uniform(75.0, 95.0), 2)
            }

            save_listing(listing)
            print(f"Saved: {listing['title']} (${listing['price']}) from {city}")

        except Exception as e:
            print(f"Error parsing listing from {city}: {e}")

def run_scraper():
    init_db()
    for city in CITIES:
        print(f"Scraping: {city}")
        html = scrape_search_page(city)
        if html:
            parse_and_save(city, html)

if __name__ == "__main__":
    run_scraper()
