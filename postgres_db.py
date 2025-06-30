
import os
import psycopg2
import json

def get_connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise Exception("DATABASE_URL not set")
    return psycopg2.connect(url, sslmode="require")

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id TEXT PRIMARY KEY,
            title TEXT,
            price REAL,
            category TEXT,
            deal_score REAL,
            location TEXT,
            url TEXT,
            ebay_average_price REAL,
            savings_amount REAL,
            savings_percentage REAL,
            image_urls TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_listing(listing):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO listings (id, title, price, category, deal_score, location, url,
            ebay_average_price, savings_amount, savings_percentage, image_urls)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            price = EXCLUDED.price,
            category = EXCLUDED.category,
            deal_score = EXCLUDED.deal_score,
            location = EXCLUDED.location,
            url = EXCLUDED.url,
            ebay_average_price = EXCLUDED.ebay_average_price,
            savings_amount = EXCLUDED.savings_amount,
            savings_percentage = EXCLUDED.savings_percentage,
            image_urls = EXCLUDED.image_urls
    """, (
        listing["id"], listing["title"], listing["price"], listing["category"],
        listing["deal_score"], listing["location"], listing["url"],
        listing["ebay_average_price"], listing["savings_amount"],
        listing["savings_percentage"], json.dumps(listing["image_urls"])
    ))
    conn.commit()
    cur.close()
    conn.close()

def fetch_top_deals(limit=20, min_score=0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, price, category, deal_score, location, url,
            ebay_average_price, savings_amount, savings_percentage, image_urls
        FROM listings
        WHERE deal_score >= %s
        ORDER BY deal_score DESC
        LIMIT %s
    """, (min_score, limit))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{
        "id": row[0],
        "title": row[1],
        "price": row[2],
        "category": row[3],
        "deal_score": row[4],
        "location": row[5],
        "url": row[6],
        "ebay_average_price": row[7],
        "savings_amount": row[8],
        "savings_percentage": row[9],
        "image_urls": json.loads(row[10])
    } for row in rows]
