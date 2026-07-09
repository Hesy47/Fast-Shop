<div align="center">

# 🛒 Fast-Shop

### A fully asynchronous, production-grade E-Commerce REST API

Built with **FastAPI**, **PostgreSQL**, **Redis**, and **Celery** — end to end async, from HTTP routes down to the database driver.

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Async-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Async-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-Cache%20%26%20Broker-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-Task%20Queue-37814A?style=for-the-badge&logo=celery&logoColor=white)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

</div>

---

## 📖 Overview

**Fast-Shop** is a fully asynchronous REST API for an online shop, built to mirror what a real production e-commerce backend looks like — not just a CRUD demo. Every layer of the stack, from the HTTP routes to the database queries, background jobs, and caching, is non-blocking and async-first, using the latest stable versions of Python and FastAPI.

The goal of this project was to practice and demonstrate real-world backend architecture: clean separation of concerns, async database sessions, distributed background processing, caching strategy, and containerized deployment.

> 💡 **Why this project?** Most tutorial-level FastAPI projects stop at "sync SQLAlchemy + SQLite." Fast-Shop goes further — async SQLAlchemy with PostgreSQL, async Redis for caching, Celery workers for heavy/delayed jobs, and FastAPI's own `BackgroundTasks` for lightweight fire-and-forget work — the kind of split you'd actually design in production.

---

## ✨ Features

- 🔐 **Authentication & Authorization** — JWT-based auth with access/refresh tokens and role-based access control
- 👤 **User Profiles** — registration, login, profile management, password handling
- 🛍️ **Product Catalog** — categories, search, filtering, and pagination
- 🛒 **Shopping Cart** — add/update/remove items, persistent per-user cart
- 📦 **Orders & Checkout** — order creation, status tracking, order history
- ⚡ **Redis Caching** — hot read-paths (catalog, product details) cached asynchronously
- 🧵 **Background Processing** — Celery + Redis for heavier async jobs (e.g. emails, order processing), FastAPI `BackgroundTasks` for lightweight fire-and-forget work
- 🗄️ **Fully Async Database Layer** — SQLAlchemy 2.0 async ORM with async sessions and migrations
- 🐳 **Containerized** — one-command local setup with Docker & docker-compose
- 📑 **Auto-generated API Docs** — interactive Swagger UI / ReDoc out of the box via FastAPI

---

## 🏗️ Tech Stack

| Layer | Technology |
|---|---|
| **Language** | Python 3.12 |
| **Framework** | FastAPI (async) |
| **Database** | PostgreSQL |
| **ORM** | SQLAlchemy 2.0 (async) |
| **Migrations** | Alembic |
| **Caching** | Redis (async) |
| **Task Queue** | Celery + Redis (broker), FastAPI `BackgroundTasks` for lightweight jobs |
| **Auth** | JWT (OAuth2 password flow) |
| **Validation** | Pydantic v2 |
| **Containerization** | Docker & Docker Compose |
| **Server** | Uvicorn / Gunicorn (ASGI) |

---

## 🧩 Architecture

```
Client
  │
  ▼
FastAPI (async routes)
  │
  ├──► SQLAlchemy (async) ──► PostgreSQL
  │
  ├──► Redis ──► Cache (products, sessions, rate limits)
  │
  └──► Celery Worker ──► Redis (broker) ──► Long-running jobs
                                             (emails, order processing, etc.)
```

Every request path — from receiving the HTTP call to querying the database, checking the cache, and dispatching background work — runs on the async event loop with no blocking I/O.

---

## 📂 Project Structure

```
fast-shop/
├── app/
│   ├── api/                # Route definitions (versioned)
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── products.py
│   │   │   ├── cart.py
│   │   │   └── orders.py
│   ├── core/                # Config, security, dependencies
│   ├── db/                  # Async session, base models
│   ├── models/               # SQLAlchemy models
│   ├── schemas/               # Pydantic schemas
│   ├── services/               # Business logic
│   ├── tasks/                    # Celery tasks
│   └── main.py                    # App entrypoint
├── alembic/                # DB migrations
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

> ℹ️ Adjust this tree to match your actual folder layout before publishing.

---

## 🚀 Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) & Docker Compose
- (Optional, for local dev without Docker) Python 3.12+, PostgreSQL, Redis

### Run with Docker (recommended)

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/fast-shop.git
cd fast-shop

# 2. Set up environment variables
cp .env.example .env

# 3. Build and start all services (API, PostgreSQL, Redis, Celery worker)
docker-compose up --build
```

The API will be available at **http://localhost:8000**
Interactive docs: **http://localhost:8000/docs** (Swagger) or **http://localhost:8000/redoc**

### Run locally (without Docker)

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run database migrations
alembic upgrade head

# 4. Start the API
uvicorn app.main:app --reload

# 5. In a separate terminal, start the Celery worker
celery -A app.tasks.celery_app worker --loglevel=info
```

---

## ⚙️ Environment Variables

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://user:pass@db:5432/fastshop` |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `SECRET_KEY` | JWT signing secret | `your-secret-key` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifetime | `30` |
| `CELERY_BROKER_URL` | Celery broker (Redis) | `redis://redis:6379/1` |

> Fill in the exact variables from your `.env.example` before publishing.

---

## 📡 API Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/auth/register` | Register a new user |
| `POST` | `/api/v1/auth/login` | Login and receive JWT tokens |
| `GET` | `/api/v1/users/me` | Get current user profile |
| `GET` | `/api/v1/products` | List/search products |
| `POST` | `/api/v1/cart` | Add item to cart |
| `GET` | `/api/v1/cart` | View current cart |
| `POST` | `/api/v1/orders` | Place an order from the cart |
| `GET` | `/api/v1/orders/{id}` | Get order status/details |

> Full, always-up-to-date documentation is available via Swagger UI at `/docs` once the app is running.

---

## 🧪 Testing

```bash
pytest -v
```

> Add details here on your test setup (pytest-asyncio, test database, coverage tooling, etc.) if applicable.

---

## 🗺️ Roadmap

- [ ] Payment gateway integration
- [ ] Product reviews & ratings
- [ ] Admin dashboard endpoints
- [ ] Rate limiting
- [ ] CI/CD pipeline (GitHub Actions)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

Built with ❤️ and `async def` by **[Your Name]**

[GitHub](https://github.com/<your-username>) · [LinkedIn](https://linkedin.com/in/<your-profile>)

</div>
