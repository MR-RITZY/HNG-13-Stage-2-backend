````markdown
# 🌍 Country Currency & Exchange API — Implementation Overview

## 🚀 Project Summary
This project is a **FastAPI-based asynchronous backend API** designed to fetch, process, and cache global country and currency data.  
It integrates with two external APIs to obtain real-time country and exchange rate information, computes an estimated GDP for each country, stores the data in a MySQL database, and provides RESTful endpoints for querying and visualization.

---

## 🧠 Architectural Approach & Design Decisions

### 1. **Choice of Stack**
- **FastAPI** — chosen for its high performance, async support, and automatic API documentation.
- **SQLAlchemy (async)** — used as ORM for database interaction, with **aiomysql** as the async database driver.
- **httpx** — for efficient asynchronous HTTP requests to the external APIs.
- **Pillow (PIL)** — for generating a summary image displaying refresh statistics.
- **MySQL** — as the persistent store for cached data, easily managed in Docker.

These choices provide a solid balance between **speed**, **clarity**, and **scalability**.

---

## 🧩 How the Problem Was Solved

### 2. **Database Layer**
The core ORM model is **`CurrencyExchange`**, representing each country record.  
It stores country details, exchange rates, computed GDP, and timestamps.

All string fields (`name`, `capital`, `region`) are stored in lowercase for **case-insensitive matching**.

Example schema:
```python
class CurrencyExchange(Base):
    __tablename__ = "currency_exchange"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    capital = Column(String(255))
    region = Column(String(255))
    population = Column(BigInteger, nullable=False)
    currency_code = Column(String(10), nullable=False)
    exchange_rate = Column(Float)
    estimated_gdp = Column(Float)
    flag_url = Column(String(255))
    last_refreshed_at = Column(DateTime, default=datetime.utcnow)
````

---

### 3. **Service Layer Design**

A dedicated class — **`CurrencyExchangeService`** — handles all external data fetching, transformation, and database interaction.

Responsibilities:

* Fetch country and exchange rate data asynchronously using `httpx.AsyncClient`
* Match currency codes with rates
* Compute GDP using:

  ```python
  estimated_gdp = population * random.uniform(1000, 2000) / exchange_rate
  ```
* Insert or update records (upsert logic)
* Trigger image generation after successful refresh

This **service-based design** keeps routes clean and makes the system easy to extend and test.

---

### 4. **Asynchronous External API Fetch**

Both external API requests are done concurrently using **httpx**.
Each call has timeout handling and raises custom errors if the source is unavailable.
On failure, a `503 Service Unavailable` response is returned, ensuring the database remains unchanged.

---

### 5. **Update and Insert Logic**

When `/countries/refresh` is called:

* Existing countries are matched by lowercase name.
* If a match is found → the record is updated (including recomputing GDP).
* If not found → a new record is inserted.
* If currency or rate data is missing → record is stored with `None` values but kept for completeness.

This ensures a **robust caching layer** that can recover from partial data availability.

---

### 6. **Image Generation and Caching**

After every successful refresh, the app generates a summary image with:

* Total number of cached countries
* Top 5 countries by GDP
* Timestamp of the last refresh

It’s saved at `cache/summary.png` using Pillow (`ImageDraw` and `ImageFont`).
The `/countries/image` endpoint simply serves this file if it exists, or returns an error JSON if not.

---

### 7. **Endpoints**

| Method     | Endpoint             | Description                                                                    |
| ---------- | -------------------- | ------------------------------------------------------------------------------ |
| **POST**   | `/countries/refresh` | Fetch, compute, and cache all data                                             |
| **GET**    | `/countries`         | Retrieve all cached countries (supports `region`, `currency`, and GDP sorting) |
| **GET**    | `/countries/{name}`  | Retrieve a single country by name                                              |
| **DELETE** | `/countries/{name}`  | Delete a country record                                                        |
| **GET**    | `/status`            | Show total countries and last refresh timestamp                                |
| **GET**    | `/countries/image`   | Serve the generated summary image                                              |

All responses are JSON with consistent formats and correct HTTP status codes.

---

### 8. **Error Handling Strategy**

Custom exceptions were created to maintain consistent response structures:

* `400 Bad Request` → Validation failure
* `404 Not Found` → Missing country
* `503 Service Unavailable` → External API failure
* `500 Internal Server Error` → Unexpected exception fallback

This pattern ensures reliability and predictability in client behavior.

---

### 9. **Performance and Reliability Enhancements**

* Full asynchronous flow from HTTP → DB → external APIs
* Uses a single exchange rate API call per refresh for efficiency
* Performs in-memory transformation before committing to DB
* Random GDP ensures a dynamic dataset each refresh
* Thread-safe and non-blocking thanks to async SQLAlchemy sessions

---

### 10. **Deployment Readiness**

The project is deployment-ready on any ASGI-compatible platform.
Developed primarily with **Railway** in mind, but easily adaptable to:

* **Heroku** (via Gunicorn + Uvicorn worker)
* **AWS ECS / Lambda**
* **Docker Compose** for local dev (`mysql:latest` container)

---

## 🧪 Local Setup Instructions

```bash
# Clone the repo
git clone https://github.com/<your-username>/country-currency-api.git
cd country-currency-api

# Create environment file
echo "DATABASE_URL=mysql+aiomysql://user:password@localhost:3306/country_cache_db" > .env
echo "PORT=8000" >> .env

# Use Poetry to install dependencies
poetry install
```

---

## Running Locally

```bash
# Activate poetry shell
poetry shell

# Run the app
uvicorn app.main:app --reload
```
---

## 🧭 Key Takeaways

* Fully **asynchronous architecture** (FastAPI + SQLAlchemy + httpx)
* Strong separation of concerns using a **service layer**
* Robust **error handling** and JSON response consistency
* Case-insensitive data management for all lookups
* Automatic **visual summary generation** after each refresh
* Structured for **production scalability**

---

## 📜 Author

**Faruq Alabi Bashir**
*Backend Engineer — passionate about clean async systems and RESTful API design.*

---