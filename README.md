# FastAPI IoT Device Management API

A production-ready, high-performance RESTful API built with **FastAPI**, **SQLAlchemy 2.0**, **Pydantic v2**, and **Alembic** to manage IoT devices and telemetry records.

The project adheres to a clean, layered architecture separating routing, business logic, data persistence, and schemas.

---

## 🚀 Key Features

- **Layered Clean Architecture**:
  - **API Layer (`app/api`)**: Endpoints with dependency injection and OpenAPI documentation.
  - **Service Layer (`app/services`)**: Business logic, transaction orchestration, and domain validation.
  - **Repository Layer (`app/repositories`)**: Encapsulated SQLAlchemy 2.0 database queries.
  - **Data Models (`app/models`)**: Declarative SQLAlchemy models with foreign key cascades.
  - **Schemas (`app/schemas`)**: Strict Pydantic v2 validation and serialization models.
- **Database & Migrations**:
  - SQLAlchemy 2.0 ORM with SQLite (default) and PostgreSQL compatibility (`psycopg2-binary`).
  - Schema migrations powered by Alembic with SQLite batch-mode support enabled.
- **Observability & Middleware**:
  - Request context middleware injecting `X-Request-ID` and measuring response latency.
  - Structured, centralized application logging (`app/core/logging.py`).
- **Error Handling**:
  - Centralized domain exception handlers (`NotFoundError`, `ConflictError`, `BusinessValidationError`) producing uniform JSON error responses.
- **Code Quality & Testing**:
  - Unit and integration tests using `pytest`, `pytest-cov`, and FastAPI `TestClient`.
  - Sub-second code formatting and linting with `ruff`.
  - Static type checking with `mypy`.

---

## 📁 Project Structure

```text
├── app/
│   ├── __init__.py
│   ├── main.py                     # FastAPI application factory, middleware, exception handlers
│   ├── core/
│   │   ├── config.py               # Pydantic Settings and environment configuration
│   │   ├── exceptions.py           # Custom application error hierarchy
│   │   └── logging.py              # Centralized logging configuration
│   ├── db/
│   │   └── session.py              # SQLAlchemy engine, declarative Base, and DB session dependency
│   ├── models/
│   │   ├── device.py               # Device database model
│   │   └── telemetry.py            # TelemetryRecord database model
│   ├── schemas/
│   │   ├── common.py               # Shared API response models
│   │   ├── device.py               # Device create/read/update schemas
│   │   └── error.py                # Standardized error payload schema
│   ├── repositories/
│   │   └── device_repository.py    # Database CRUD operations
│   ├── services/
│   │   └── device_service.py       # Business logic and validation rules
│   └── api/
│       ├── deps.py                 # Endpoint dependency providers
│       └── v1/
│           ├── router.py           # Aggregated v1 API router
│           └── endpoints/
│               ├── devices.py      # Device management endpoints
│               └── health.py       # Health check endpoint
├── alembic/
│   ├── env.py                      # Alembic runtime environment (configured with batch mode)
│   └── versions/                   # Versioned database migration scripts
├── tests/
│   ├── conftest.py                 # Pytest fixtures, in-memory DB setup, and test client
│   ├── integration/
│   │   └── test_devices_api.py     # End-to-end API integration tests
│   └── unit/
│       └── test_device_service.py  # Service-level business logic tests
├── .env.example                    # Sample environment variables template
├── .gitignore                      # Git ignore rules for Python, virtual environments, and SQLite
├── alembic.ini                     # Alembic configuration
├── pytest.ini                      # Pytest and coverage settings
├── requirements.txt                # Pinned production and development dependencies
└── README.md                       # Project documentation
```

---

## 🛠️ Getting Started

### Prerequisites

- Python 3.10+ (Python 3.12 recommended)
- `pip` and `venv`

### 1. Clone & Set Up Virtual Environment

```bash
git clone https://github.com/vaibhavambavkar1/fastapi_iot_App.git
cd fastapi_iot_App

python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root (or copy `.env.example`):

```bash
cat << 'EOF' > .env
IOT_APP_NAME="IoT Device API"
IOT_ENVIRONMENT=local
IOT_DEBUG=true
IOT_DATABASE_URL=sqlite:///./iot.db
IOT_LOG_LEVEL=INFO
IOT_API_V1_PREFIX=/api/v1
EOF
```

---

## 🗄️ Database Migrations (Alembic)

Database schema is managed using Alembic.

### Apply Migrations
Apply all migrations up to the latest revision:
```bash
alembic upgrade head
```

### Generate a New Migration
When making changes to models in `app/models/`:
```bash
alembic revision --autogenerate -m "describe your changes"
```

### Roll Back a Migration
```bash
# Roll back the most recent migration:
alembic downgrade -1

# View migration history:
alembic history --verbose
```

> **Note on SQLite**: `alembic/env.py` is preconfigured with `render_as_batch=True` to support SQLite column modifications (`ALTER TABLE`) without errors.

---

## ⚡ Running the Application

Start the development server with live reload:

```bash
uvicorn app.main:app --reload --port 8000
```
*(If port 8000 is occupied by another service on your system, use an alternate port like `--port 8080`.)*

### 📖 Interactive API Documentation

Once running, access the auto-generated documentation in your browser:

- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
- **OpenAPI Schema (JSON)**: [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

## 📡 API Endpoints Overview

All routes are prefixed with `/api/v1`.

| Method | Path | Description | Status Code |
|---|---|---|---|
| `GET` | `/api/v1/health` | Health check endpoint | `200 OK` |
| `POST` | `/api/v1/devices` | Register a new IoT device | `201 Created` |
| `GET` | `/api/v1/devices` | List devices with pagination (`skip`, `limit`) | `200 OK` |
| `GET` | `/api/v1/devices/{device_id}` | Retrieve device details by ID | `200 OK` |
| `PATCH` | `/api/v1/devices/{device_id}` | Update device attributes | `200 OK` |
| `DELETE`| `/api/v1/devices/{device_id}` | Delete a device and cascade-delete telemetry | `204 No Content` |
| `GET` | `/api/v1/devices/{device_id}/telemetry/export` | **Generator Stream:** Export telemetry data (`?format=csv` or `?format=json`) | `200 OK` |
| `GET` | `/api/v1/devices/{device_key}/telemetry/live` | **Async Generator (SSE):** Live real-time sensor events (`text/event-stream`) | `200 OK` |
| `POST` | `/api/v1/devices/{device_id}/telemetry/ingest` | **Generator Ingest:** Line-by-line streaming CSV bulk ingestion | `201 Created` |

### Sample Generator Requests

#### 1. Ingest Large Telemetry CSV Stream
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/devices/1/telemetry/ingest" \
  -H "Content-Type: text/csv" \
  --data-binary "metric,value
temperature,25.4
humidity,62.1
voltage,3.32"
```

#### 2. Stream Export Telemetry Records (CSV or NDJSON)
```bash
# Stream as CSV:
curl -N "http://127.0.0.1:8000/api/v1/devices/1/telemetry/export?format=csv"

# Stream as Newline-Delimited JSON (NDJSON):
curl -N "http://127.0.0.1:8000/api/v1/devices/1/telemetry/export?format=json"
```

#### 3. Stream Live Device Events via SSE
```bash
curl -N "http://127.0.0.1:8000/api/v1/devices/sensor-001/telemetry/live"
```

### Sample Request: Register Device

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/devices" \
  -H "Content-Type: application/json" \
  -d '{
    "device_key": "temp-sensor-001",
    "name": "Warehouse Temperature Sensor",
    "device_type": "sensor",
    "status": "active"
  }'
```

---

## 🧪 Testing & Code Quality

### Running Tests

Run the test suite with coverage enabled:

```bash
pytest
```

Run tests with verbose output:
```bash
pytest -v
```

Generate an HTML coverage report:
```bash
pytest --cov-report=html
# Open htmlcov/index.html in your browser
```

### Linting & Formatting

Format code using Ruff:
```bash
ruff format .
```

Run linter checks and auto-fix safe issues:
```bash
ruff check --fix .
```

### Static Type Checking

Check type annotations using Mypy:
```bash
mypy app
```
