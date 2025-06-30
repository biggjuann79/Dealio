import os
import psycopg2

def get_connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise Exception("DATABASE_URL environment variable is not set")
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
            url TEXT
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

def save_listing(listing):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO listings (id, title, price, category, deal_score, url)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE SET
            title = EXCLUDED.title,
            price = EXCLUDED.price,
            category = EXCLUDED.category,
            deal_score = EXCLUDED.deal_score,
            url = EXCLUDED.url
    """, (
        listing["id"],
        listing["title"],
        listing["price"],
        listing["category"],
        listing["deal_score"],
        listing["url"]
    ))
    conn.commit()
    cur.close()
    conn.close()

def fetch_top_deals(limit=20, min_score=70.0):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, title, price, category, deal_score, url
        FROM listings
        WHERE deal_score >= %s
        ORDER BY deal_score DESC
        LIMIT %s
    """, (min_score, limit))
    results = []
    for row in cur.fetchall():
        results.append({
            "id": row[0],
            "title": row[1],
            "price": row[2],
            "category": row[3],
            "deal_score": row[4],
            "url": row[5]
        })
    cur.close()
    conn.close()
    return results
