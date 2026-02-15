from fastapi import FastAPI, HTTPException
from . import schemas
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List


app = FastAPI()

def get_db_connection():
    db_params = {
        "host" : "db",
        "database": "hoopp_intelligence",
        "user": "admin",
        "password" : "password123",
        "port": "5432"
    }

    try:
        return psycopg2.connect(**db_params, cursor_factory=RealDictCursor)
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error connecting to the database or executing query: {error}")


app.get("/")
def health():
    return {"status": "ok"} 

app.get("/news", response_model=List[schemas.MarketNews])
def get_news(limit: int = 50, sentiment_filter: str = "all"):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    curr = conn.cursor()

    query = "SELECT m.id, m.headline, m.sentiment_score, p.asset_class, m.captured_at " \
    "FROM market_intelligence AS m " \
    "INNER JOIN portfolio_targets ON m.asset_class_id = portfolio_targets.id " \
    ""

    
    
    results = curr.fetchall()
    conn.commit()
    curr.close()
    conn.close()

    return results