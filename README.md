# URL Shortener Service

This is a FastAPI-based URL Shortener service with click analytics, rate limiting and custom aliases

## Features
- Create short URLs with optional TTL (expiry)
- Redirect via short codes
- Capture click analytics (IP, user agent, timestamp)
- Retrieve analytics for a short URL
- Rate limiting and custom aliases

## Setup Instructions

### 0. Prerequisites
- Python 3.10+
- (Optional) Install `uv` for faster dependency management:
- Git

### 1. Clone the repository
```bash
git clone https://github.com/Ian-Mc-Okeyo/URL-Shortener.git
cd url-shortener
```

### 2. Create & activate a virtual environment

#### Using uv (recommended)
```bash
uv venv .venv
source .venv/bin/activate
```

#### Using Python built-in venv (Linux/macOS)
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Using Python built-in venv (Windows PowerShell / CMD)
```powershell
python -m venv .venv
.venv\Scripts\activate
```

#### Verify activation
```bash
python -V
which python    # Linux/macOS
where python    # Windows
```
You should see the interpreter path inside `.venv`.

#### Deactivate when done
```bash
deactivate
```

### 3. Install dependencies
If you use [uv] (recommended for speed):
```bash
uv pip install
```
Editable install with pip (if `pyproject.toml` present):
```bash
pip install -e .
```
Or from a locked list (if `requirements.txt` present):
```bash
pip install -r requirements.txt
```

### 4. Database Migrations (Alembic)
Alembic is already configured. After pulling new migrations, upgrade the database schema with:
```bash
alembic upgrade head
```
If you later need to generate a new migration (after changing models):
```bash
alembic revision -m "describe change" --autogenerate
alembic upgrade head
```
Ensure your virtual environment is active and the database URL is set appropriately in `alembic.ini` or environment variables before running these commands.

### 5. Run the application
```bash
uvicorn main:app --reload
```
By default, the app will be available at [http://localhost:8000](http://localhost:8000)

### 6. API Documentation
Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

### 7. Running Tests
```bash
pytest
```

## Project Structure

- `main.py` — Entry point for FastAPI app
- `app/` — Application code (routes, core, models, schemas and utils.)
- `tests/` — Pytest test cases
- `pyproject.toml` — Project metadata and dependencies

## Example Usage

**Create a short URL:**
```bash
curl -X POST http://localhost:8000/shorten \
	-H 'Content-Type: application/json' \
	-d '{"original_url": "https://example.com", "ttl_seconds": 600, "alias": "ex"}'
```

**Redirect:**
```bash
curl -i http://localhost:8000/ex
```

**Get analytics:**
```bash
curl http://localhost:8000/analytics/ex
```

## Notes
- For development, the in-memory rate limiter and database are not production-ready.
- For production, use a persistent database and distributed rate limiting (e.g., Redis).
- See code comments and docstrings for more details.

## Scaling Considerations
**Traffic & Concurrency**: Redirect reads dominate; We can cache short codes (Redis / in-memory LRU) and run multiple async workers behind a load balancer.

**Data Storage**: Use Postgres (unique index on `short_code`); Currently this application uses SQLite because it's a testing environemnt. Also we can consider database partitioning or time-series DB for large click volumes; Old events can also be archived to reduce the number of rows on DB.

**Caching**: Short code: destination URL cached with TTL; negative caching for misses;

**Rate Limiting & Abuse**: Distributed counters; stricter creation limits; bot detection and optional CAPTCHA for bulk creators.

**Analytics Pipeline**: Async click logging via queue via Kafka; batch inserts; periodic pre-aggregation for fast analytics responses;.

**Expiration & Cleanup**: Scheduled job to remove expired links and evict cache; minimize index bloat.

**Security**: URL validation, domain allow/deny lists, secrets via env/manager, observability for spikes in 429 or errors. For now, since it is a test enviroment, I have allowed all origins.

**Cost Optimization**: Pre-aggregate analytics to reduce heavy on-demand queries.
