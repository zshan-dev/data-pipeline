# Market Intelligence Engine

**A real-time Data Engineering platform that automates risk monitoring and sentiment analysis for institutional portfolios.**

---

### Summary

The **Intelligence Engine** is a production-grade ETL (Extract, Transform, Load) solution designed to modernize risk monitoring. Addressing the limitations of legacy quarterly reporting, this engine ingests **forward-looking market signals** in real-time.

The system autonomously maps unstructured news data to specific asset allocations (e.g., Real Estate, Private Equity), applies NLP sentiment analysis to generate early warning signals, and exposes this intelligence via a high-performance **REST API** for downstream consumption.

---

### Key Impact & Quantifiable Metrics

* **99% Latency Reduction:** Transformed risk monitoring from a **90-day lag** (quarterly reports) to **Real-Time** (continuous ingestion), allowing for immediate reaction to market events.
* **Automated Scalability:** Simultaneously monitors **6+ major asset classes** across thousands of daily news sources, automating a workload equivalent to **10+ full-time analysts**.
* **Deployment Efficiency:** Implemented Docker & Infrastructure-as-Code to reduce developer environment setup time from ~1 hour to **<5 minutes**.
* **Data Accessibility:** Built a **FastAPI** microservice to serve risk metrics to frontend dashboards, decoupling data processing from data visualization.

---

### Architecture & Tech Stack

The system utilizes a microservices-based architecture to ensure modularity, fault tolerance, and separation of concerns.

#### **The Stack**

* **Core Logic:** Python 3.10 (Data Ingestion & NLP)
* **API Framework:** FastAPI (High-Performance Async REST Interface)
* **Database:** PostgreSQL 15 (Relational Data Storage)
* **Containerization:** Docker & Docker Compose (Orchestration)
* **Libraries:** `psycopg2`, `feedparser`, `vaderSentiment`, `uvicorn`

#### **The Data Lifecycle**

1. **Extract (Source):** The Ingestor queries the database for high-priority asset classes based on risk profile.
2. **Transform (Analysis):** It fetches real-time market news via RSS and processes headlines through a **VADER Sentiment Engine** to assign polarity scores (-1.0 to +1.0).
3. **Load (Storage):** Structured data is stored in a PostgreSQL data warehouse.
4. **Serve (Delivery):** A **FastAPI** layer exposes these risk scores via JSON endpoints, allowing external dashboards to query "Real-Time Sentiment" without direct database access.

---

### Core Features 

* **API-First Design:** Uses FastAPI to provide a standard, documented interface (Swagger UI) for accessing data, making the backend "frontend-agnostic."
* **Dynamic Ingestion:** Automatically adapts search queries based on the active portfolio mix stored in the database.
* **NLP Sentiment Scoring:** Algorithmically judges news as Positive, Neutral, or Negative to quantify market mood.
* **Containerized Environment:** Fully portable development environment ensuring 100% consistency across machines.
