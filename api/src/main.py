from fastapi import FastAPI

import psycopg2

app = FastAPI()

def query_postgres():
    db_params = {
        "host" : "localhost",
        "database": "hoopp-db",
        "user": "admin",
        "password" : "password123",
        "port": "5432"
    }
    conn = None
    cursor = None

    try:
        conn = psycopg2.connect(**db_params)
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error connecting to the database or executing query: {error}")


app.get("/")
def health():
    return {"status": "ok"} 

app.get("/news")
def get_news(data:str, limit : int, filter: str):
    # SELECT * FROM market_intelligence
    pass 