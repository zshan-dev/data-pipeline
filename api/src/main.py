from fastapi import FastAPI, HTTPException
from . import models
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

app.get("/news", response_model=List[models.MarketNews])
def get_news(limit: int = 50, sentiment_filter: str = "all"):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    curr = conn.cursor()

    query = " "

    results = curr.fetchall()
    conn.commit()
    curr.close()
    conn.close()

    return results