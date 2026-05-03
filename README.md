# ShopRAG

A RAG-powered shop price comparison and dynamic price update system built with FastAPI, SQLAlchemy, Qdrant, and DuckDuckGo Search.

## Features

- 🛍️ **Product Management** — Full CRUD via REST API
- 🔍 **Web Search** — DuckDuckGo-powered similar product discovery
- 🧠 **Vector Embeddings** — Qdrant stores product embeddings for semantic similarity
- 💰 **Dynamic Pricing** — Automatically suggests price updates based on market data
- 🖥️ **Admin Panel** — Built-in SQLAdmin panel at `/admin`
- 📋 **Structured Logging** — Loguru with file rotation
- 🐳 **Dockerized** — Full docker-compose setup

## Architecture

Hexagonal (ports & adapters) architecture:

```
app/
├── core/           # Domain models and port interfaces
│   ├── domain/     # Product, SimilarProduct dataclasses
│   └── ports/      # Abstract repository and searcher interfaces
├── adapters/       # Concrete implementations
│   ├── db/         # SQLAlchemy (PostgreSQL)
│   ├── vector_store/ # Qdrant
│   └── web_search/ # DuckDuckGo
├── services/       # Business logic
└── api/            # FastAPI routes and dependency injection
```

## Quick Start

### With Docker Compose

```bash
cp .env.example .env
docker-compose up --build
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Admin**: http://localhost:8000/admin
- **Health**: http://localhost:8000/health

### Local Development

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start PostgreSQL and Qdrant (via Docker)
docker-compose up db qdrant -d

# Run the app
uvicorn app.main:app --reload
```

## API Endpoints

### Products

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/products/` | List all products |
| GET | `/api/v1/products/{id}` | Get a product |
| POST | `/api/v1/products/` | Create a product |
| DELETE | `/api/v1/products/{id}` | Delete a product |

### Price Updates

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/price-updates/{id}/search` | Search and store similar products |
| GET | `/api/v1/price-updates/{id}/similar` | Get stored similar products |
| POST | `/api/v1/price-updates/{id}/update` | Update product price based on market data |
| POST | `/api/v1/price-updates/bulk-update` | Bulk update all product prices |

## Configuration

All configuration is via environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://shoprag:shoprag@db:5432/shoprag` | PostgreSQL connection |
| `QDRANT_HOST` | `qdrant` | Qdrant hostname |
| `QDRANT_PORT` | `6333` | Qdrant port |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `PRICE_UPDATE_MARGIN` | `0.05` | Acceptable price deviation (5%) |
| `MAX_SEARCH_RESULTS` | `5` | Max web search results per query |
| `SECRET_KEY` | — | Admin panel secret key |

## Running Tests

```bash
pytest tests/ -v
```

## Database Migrations

```bash
# Create a migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head
```

## CI/CD

GitHub Actions workflow (`.github/workflows/ci-cd.yml`):
- **Tests** run on every push and PR
- **Docker image** built and pushed to GHCR on `main` branch pushes
- **Releases** created automatically for version tags (`v*`)
  - Tags with `-alpha`, `-beta`, `-nightly` → staging pre-release
  - Clean version tags → production release
