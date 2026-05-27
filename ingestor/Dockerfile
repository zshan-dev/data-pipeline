FROM python:3.10-slim

WORKDIR /app

# Java is required by PySpark (Spark runs on the JVM).
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libpq-dev gcc default-jre-headless wget && \
    rm -rf /var/lib/apt/lists/*

# PostgreSQL JDBC driver — Spark uses this to write to Postgres via JDBC.
RUN wget -q -O /opt/postgresql.jar \
    https://jdbc.postgresql.org/download/postgresql-42.7.3.jar

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

CMD ["tail", "-f", "/dev/null"]
