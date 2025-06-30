
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from postgres_db import fetch_top_deals, init_db

app = FastAPI()

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
        return {"status": "healthy"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/deals")
def deals(limit: int = 20, min_score: float = 0):
    try:
        results = fetch_top_deals(limit, min_score)
        return {"success": True, "data": results, "count": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
