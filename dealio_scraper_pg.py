
import requests
from bs4 import BeautifulSoup
import hashlib
import time
from datetime import datetime
from postgres_db import save_listing, init_db
from ebay_lookup import lookup_ebay_price, calculate_deal_score

CITIES = [
    "newyork", "losangeles", "chicago", "houston", "phoenix",
    "philadelphia", "sanantonio", "sandiego", "dallas", "sanjose"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def generate_listing_id(url):
    return hashlib.md5(url.encode()).hexdigest()

def scrape_search_page(city):
    base_url = f"https://{city}.craigslist.org/search/sss"
    response = requests.get(base_url, headers=HEADERS)
    soup = BeautifulSoup(response.text, "html.parser")
    listings = soup.find_all("li", class_="result-row")

    extracted = []
    for li in listings[:10]:  # limit per city
        try:
            title_tag = li.find("a", class_="result-title")
            price_tag = li.find("span", class_="result-price")
            date_tag = li.find("time", class_="result-date")

            url = title_tag["href"]
            price = float(price_tag.text.strip("$")) if price_tag else 0.0
            title = title_tag.text.strip()
            created_at = date_tag["datetime"]

            extracted.append({
                "url": url,
                "title": title,
                "price": price,
                "created_at": created_at,
                "source_city": city
            })
        except Exception:
            continue

    return extracted

def scrape_full_listing(listing):
    try:
        response = requests.get(listing["url"], headers=HEADERS, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        desc = soup.find("section", {"id": "postingbody"})
        location = soup.find("div", class_="mapaddress")
        images = [img["src"] for img in soup.select("img") if "src" in img.attrs]

        listing["id"] = generate_listing_id(listing["url"])
        listing["description"] = desc.text.strip() if desc else ""
        listing["location"] = location.text.strip() if location else "Unknown"
        listing["image_urls"] = images
        listing["category"] = "general"

        ebay_price = lookup_ebay_price(listing["title"])
        if ebay_price:
            sa, sp, score = calculate_deal_score(listing["price"], ebay_price)
            listing["ebay_avg_price"] = ebay_price
            listing["savings_amount"] = sa
            listing["savings_percentage"] = sp
            listing["deal_score"] = score
        else:
            listing["ebay_avg_price"] = None
            listing["savings_amount"] = None
            listing["savings_percentage"] = None
            listing["deal_score"] = None

        return listing
    except Exception as e:
        print(f"Error fetching full post: {listing['url'][:50]}... - {e}")
        return None

def run_scraper():
    init_db()
    for city in CITIES:
        print(f"🌆 Scraping: {city}")
        results = scrape_search_page(city)
        for item in results:
            full = scrape_full_listing(item)
            if full:
                save_listing(full)
                print(f"✅ {full['title'][:35]} | Score: {full['deal_score']}")
            time.sleep(1)

if __name__ == "__main__":
    run_scraper()
