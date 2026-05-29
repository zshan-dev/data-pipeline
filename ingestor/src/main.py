import feedparser
import urllib.parse
import psycopg2
from datetime import datetime
import time

from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, lit, current_timestamp
from pyspark.sql.types import FloatType, StringType, StructField, StructType, IntegerType, TimestampType
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# VADER sentiment analyser — scores headlines -1.0 (negative) to +1.0 (positive).
analyzer = SentimentIntensityAnalyzer()

DB_HOST = "db"
DB_NAME = "hoopp_intelligence"
DB_USER = "admin"
DB_PASS = "password123"
DB_PORT = "5432"

JDBC_URL = f"jdbc:postgresql://{DB_HOST}:{DB_PORT}/{DB_NAME}"
JDBC_DRIVER = "/opt/postgresql.jar"
JDBC_PROPS = {"user": DB_USER, "password": DB_PASS, "driver": "org.postgresql.Driver"}


def get_spark() -> SparkSession:
    """Create (or reuse) the SparkSession with the Postgres JDBC driver on the classpath."""
    return (
        SparkSession.builder
        .appName("MarketIntelligenceIngestor")
        .config("spark.jars", JDBC_DRIVER)
        # Run locally — all cores on this single container.
        .config("spark.master", "local[*]")
        # Suppress verbose Spark/Hadoop INFO logs so pipeline output is readable.
        .config("spark.driver.extraJavaOptions", "-Dlog4j.logLevel=WARN")
        .getOrCreate()
    )


def get_db_connection():
    """Plain psycopg2 connection — used only for the lightweight target query."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )


def fetch_portfolio_targets():
    """Return (id, asset_class) tuples for High/Medium risk targets."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, asset_class "
        "FROM portfolio_targets "
        "WHERE LOWER(risk_level) IN ('high', 'medium');"
    )
    targets = cur.fetchall()
    cur.close()
    conn.close()
    return targets


def fetch_google_news(query):
    """Fetch up to 5 recent Google News RSS entries for a given query."""
    encoded_query = urllib.parse.quote(f"{query} market news canada")
    rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-CA&gl=CA&ceid=CA:en"
    print(f"Searching news for: {query}...")
    feed = feedparser.parse(rss_url)
    return feed.entries[:5]


def score_headline(headline: str) -> float:
    """VADER UDF: returns the compound sentiment score for a single headline."""
    try:
        return float(analyzer.polarity_scores(headline)["compound"])
    except Exception:
        return 0.0


def save_intelligence(spark: SparkSession, asset_id: int, asset_name: str, articles: list):
    """
    PySpark transform + load step.

    1. Build a Spark DataFrame from the raw article list.
    2. Apply the VADER UDF across the 'headline' column.
    3. Write the scored rows to market_intelligence via JDBC.
    """
    if not articles:
        print(f"No articles found for {asset_name}, skipping.")
        return

    # --- Build raw DataFrame ---
    schema = StructType([
        StructField("headline", StringType(), False),
        StructField("asset_class_id", IntegerType(), False),
    ])
    rows = [(article.title, asset_id) for article in articles]
    df = spark.createDataFrame(rows, schema=schema)

    # --- Transform: score every headline with VADER via UDF ---
    score_udf = udf(score_headline, FloatType())
    df = df.withColumn("sentiment_score", score_udf(df["headline"]))
    df = df.withColumn("captured_at", current_timestamp())

    # Preview scores in the console so you can see what Spark computed.
    print(f"\n  Spark DataFrame for '{asset_name}':")
    df.select("headline", "sentiment_score").show(truncate=50)

    # --- Load: write scored rows to Postgres via JDBC ---
    df.write \
        .format("jdbc") \
        .option("url", JDBC_URL) \
        .option("dbtable", "market_intelligence") \
        .option("user", DB_USER) \
        .option("password", DB_PASS) \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

    print(f"  Saved {df.count()} scored articles for '{asset_name}' (asset_id={asset_id}).")


def run_pipeline():
    print("Starting Intelligence Engine (PySpark mode)...")

    spark = get_spark()
    # Quieten Spark's own console logger after session creation.
    spark.sparkContext.setLogLevel("WARN")

    targets = fetch_portfolio_targets()
    print(f" Found {len(targets)} active targets to monitor.")

    for asset_id, asset_name in targets:
        articles = fetch_google_news(asset_name)
        save_intelligence(spark, asset_id, asset_name, articles)
        time.sleep(2)

    spark.stop()
    print("\nPipeline finished successfully.")


if __name__ == "__main__":
    time.sleep(5)

    # Uncomment to run continuously (near-real-time mode).
    # Polls every 15 minutes — change the interval as needed.
    # while True:
    #     run_pipeline()
    #     time.sleep(900)

    # Manual trigger mode (default) — run once and exit.
    run_pipeline()
