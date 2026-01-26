import feedparser
import psycopg2
import urllib.parse
from datetime import datetime
import time

DB_HOST = "db"  
DB_NAME = "hoopp_intelligence"
DB_USER = "admin"
DB_PASS = "password123"

def get_db_connection():
    """Connects to the Postgres container."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn

def fetch_portfolio_targets():
    """EXTRACT: Asks the DB what we need to monitor."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id, asset_class FROM portfolio_targets WHERE risk_level IN ('High', 'Medium');")
    targets = cur.fetchall()
    
    cur.close()
    conn.close()
    return targets

def fetch_google_news(query):
    """TRANSFORM: Searches Google News RSS for a specific topic."""
    
    encoded_query = urllib.parse.quote(f"{query} market news canada")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-CA&gl=CA&ceid=CA:en"
    
    print(f" Searching news for: {query}...")
    feed = feedparser.parse(rss_url)
    
    return feed.entries[:5] 

def save_intelligence(asset_id, articles):
    """LOAD: Saves the headlines into our database."""
    conn = get_db_connection()
    cur = conn.cursor()
    
    count = 0
    for article in articles:

        headline = article.title
        sentiment_score = 0.0 
        
        cur.execute("""
            INSERT INTO market_intelligence (headline, sentiment_score, asset_class_id, captured_at)
            VALUES (%s, %s, %s, NOW())
        """, (headline, sentiment_score, asset_id))
        count += 1
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"Saved {count} articles for Asset ID {asset_id}")

def run_pipeline():
    print(" Starting HOOPP Intelligence Engine...")
    
    targets = fetch_portfolio_targets()
    print(f" Found {len(targets)} active targets to monitor.")

    for target in targets:
        asset_id, asset_name = target
        
        news_items = fetch_google_news(asset_name)
        
        if news_items:
            save_intelligence(asset_id, news_items)
            
        time.sleep(2)

    print("🏁 Pipeline finished successfully.")

if __name__ == "__main__":
    # Wait for DB to be ready (Docker timing fix)
    time.sleep(5) 
    run_pipeline()