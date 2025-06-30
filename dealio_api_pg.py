
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from postgres_db import fetch_top_deals, init_db

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
