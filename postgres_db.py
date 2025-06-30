
import os
import psycopg2
from datetime import datetime

# Use Railway-provided DATABASE_URL or local fallback
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/dealio")

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require" if "railway" in DATABASE_URL else "disable")

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS listings (
            id TEXT PRIMARY KEY,
            title TEXT,
            price REAL,
            location TEXT,
            description TEXT,
            url TEXT,
            image_urls TEXT,
            source_city TEXT,
            category TEXT,
            created_at TEXT,
            ebay_avg_price REAL,
            savings_amount REAL,
            savings_percentage REAL,
            deal_score REAL
        )
    """)
    conn.commit()
    conn.close()

def save_listing(listing: dict):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO listings (
            id, title, price, location, description, url, image_urls,
            source_city, category, created_at, ebay_avg_price,
            savings_amount, savings_percentage, deal_score
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            price = EXCLUDED.price,
            location = EXCLUDED.location,
            description = EXCLUDED.description,
            url = EXCLUDED.url,
            image_urls = EXCLUDED.image_urls,
            source_city = EXCLUDED.source_city,
            category = EXCLUDED.category,
            created_at = EXCLUDED.created_at,
            ebay_avg_price = EXCLUDED.ebay_avg_price,
            savings_amount = EXCLUDED.savings_amount,
            savings_percentage = EXCLUDED.savings_percentage,
            deal_score = EXCLUDED.deal_score
    """, (
        listing.get("id"),
        listing.get("title"),
        listing.get("price"),
        listing.get("location"),
        listing.get("description"),
        listing.get("url"),
        ",".join(listing.get("image_urls", [])),
        listing.get("source_city"),
        listing.get("category"),
        listing.get("created_at", datetime.utcnow().isoformat()),
        listing.get("ebay_avg_price"),
        listing.get("savings_amount"),
        listing.get("savings_percentage"),
        listing.get("deal_score")
    ))
    conn.commit()
    conn.close()

def fetch_top_deals(limit=20, min_score=70.0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM listings
        WHERE deal_score >= %s
        ORDER BY deal_score DESC
        LIMIT %s
    """, (min_score, limit))
    columns = [desc[0] for desc in cursor.description]
    results = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return results
