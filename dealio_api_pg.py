from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

# -----------------------------------
# Database Functions
# -----------------------------------
def get_connection():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS listings (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT,
                    deal_score REAL,
                    location TEXT,
                    url TEXT,
                    image_urls TEXT[],
                    created_at TIMESTAMPTZ DEFAULT NOW()
                )
            """)
            conn.commit()

def fetch_top_deals(limit: int = 20, min_score: float = 70.0):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, price, category, deal_score, location, url, image_urls, created_at FROM listings WHERE deal_score >= %s ORDER BY deal_score DESC LIMIT %s",
                (min_score, limit)
            )
            rows = cur.fetchall()
            deals = []
            for row in rows:
                deals.append({
                    "id": row[0],
                    "title": row[1],
                    "price": row[2],
                    "category": row[3],
                    "deal_score": row[4],
                    "location": row[5],
                    "url": row[6],
                    "image_urls": row[7],
                    "created_at": row[8].isoformat() if row[8] else None
                })
            return deals

# -----------------------------------
# FastAPI App Setup
# -----------------------------------
app = FastAPI(
    title="Dealio API",
    description="API to serve top deals scraped from Craigslist with eBay comparison",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Dealio API is live"}

@app.get("/health")
def health():
    try:
        init_db()
        return {"status": "healthy", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/deals")
def get_deals(limit: int = 20, min_score: float = 70.0):
    try:
        results = fetch_top_deals(limit, min_score)
        return {"success": True, "data": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug/db")
def debug_db():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT NOW()")
                now = cur.fetchone()[0]
        return {"status": "connected", "timestamp": now}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
