from fastapi import FastAPI

import psycopg2

app = FastAPI()

def get_db_connection():
    db_params = {
        "host" : "localhost",
        "database": "hoopp-db",
        "user": "admin",
        "password" : "password123",
        "port": "5432"
    }

    try:
        return psycopg2.connect(**db_params)
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"Error connecting to the database or executing query: {error}")


app.get("/")
def health():
    return {"status": "ok"} 

app.get("/news")
def get_news(data:str, limit : int, filter: str):
    conn = get_db_connection()
    curr = conn.cursor
    curr.execute("SELECT %s FROM market_intelligence LIMIT 50 WHERE news = %s", data, filter)
    #psycopg2.extras.RealDictCursor

    conn.commit()
    curr.close()
    conn.close()