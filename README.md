# GL Transfer API

Production-grade FastAPI backend for the GL Transfer software.

## Project Structure

```
backend/
├── app/
│   ├── main.py                  # App factory — middleware, exception handlers, routers
│   ├── core/
│   │   ├── config.py            # Settings loaded from .env via pydantic-settings
│   │   ├── exceptions.py        # AppException hierarchy + HTTP/validation handlers
│   │   └── logging.py           # Structured stdout logging setup
│   ├── middleware/
│   │   ├── request_logger.py    # Logs every request; attaches X-Request-ID header
│   │   └── security_headers.py  # Adds X-Frame-Options, X-Content-Type-Options, etc.
│   ├── schemas/
│   │   └── responses.py         # Shared response models (SuccessResponse, ErrorResponse)
│   └── api/
│       ├── router.py            # Central API router
│       └── health.py            # GET /api/v1/health
├── requirements.txt
├── .env.example
└── README.md
```

## Requirements

- Python 3.11+

## Setup

**1. Create and activate a virtual environment**

```bash
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows
```

**2. Install dependencies**

```bash
pip install -r requirements.txt
```

**3. Configure environment**

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string — see format below |
| `SECRET_KEY` | Long random string used for token signing |
| `ALLOWED_ORIGINS` | JSON array of allowed frontend origins |
| `DEBUG` | `true` to enable `/docs`, `/redoc`, `/openapi.json` |

**Setting `DATABASE_URL`**

The connection string follows this format:

```
postgresql+psycopg2://<username>:<password>@<host>:<port>/<database_name>
```

Replace each placeholder with your PostgreSQL details:

| Placeholder | What to put here |
|---|---|
| `<username>` | The PostgreSQL login name (e.g. `postgres`) |
| `<password>` | The password for that login |
| `<host>` | Where the database is running — use `localhost` if it is on your machine |
| `<port>` | The port PostgreSQL listens on — default is `5432` |
| `<database_name>` | The name of the database created for this project |

Example:

```
DATABASE_URL=postgresql+psycopg2://postgres:mysecretpassword@localhost:5432/gl_transfer
```

## Database Migrations

Migrations are managed with [Alembic](https://alembic.sqlalchemy.org/). Run these from the project root with your virtual environment active.

**Apply all pending migrations (do this after every pull)**

```bash
alembic upgrade head
```

> If you see an error like `FATAL: database does not exist`, make sure the database named in `DATABASE_URL` has been created in PostgreSQL before running migrations.

---

## Running

**Development**

```bash
uvicorn app.main:app --reload --port 8000
```

**Production**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API

### Base URL

```
/api/v1
```

### Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | Health check — returns app name and version |

### Response Format

All responses follow a consistent envelope:

**Success**
```json
{
  "success": true,
  "data": { ... }
}
```

**Error**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Resource 'x' not found.",
    "details": null
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|---|---|---|
| `NOT_FOUND` | 404 | Resource does not exist |
| `UNAUTHORIZED` | 401 | Authentication required |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `CONFLICT` | 409 | State conflict (e.g. duplicate) |
| `VALIDATION_ERROR` | 422 | Request body/query failed validation |
| `HTTP_ERROR` | varies | Generic HTTP error |
| `INTERNAL_SERVER_ERROR` | 500 | Unhandled server error |

## Middleware

| Middleware | Purpose |
|---|---|
| `CORSMiddleware` | Restricts cross-origin requests to `ALLOWED_ORIGINS` |
| `SecurityHeadersMiddleware` | Adds `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`, `Referrer-Policy` |
| `RequestLoggerMiddleware` | Logs method, path, status, elapsed time; injects `X-Request-ID` into every response |

## Adding a New Route

1. Create `app/api/<resource>.py` with an `APIRouter`
2. Register it in `app/api/router.py` via `api_router.include_router(...)`
3. Use `SuccessResponse[YourSchema]` as the `response_model`
4. Raise `AppException` subclasses (`NotFoundException`, etc.) for domain errors
