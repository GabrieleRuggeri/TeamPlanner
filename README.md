# TeamPlanner

TeamPlanner is a lightweight web app for planning smart-working days and days off within a small team.

## Prerequisites
- Python 3.11+
- One of:
  - [uv](https://github.com/astral-sh/uv) (preferred for local dev)
  - `pip` (used in Docker builds)
- Docker + Docker Compose (optional, for containerized run)

## Dependencies
Runtime dependencies are pinned in `requirements.txt` and `pyproject.toml`:
- FastAPI, Uvicorn (API server)
- SQLModel + Pydantic settings (data + configuration)
- `psycopg2-binary` (Postgres driver for Docker deployments)

No API keys are required for local or Docker usage.

## Quick start
### Docker (app + database)
```bash
docker compose up --build
```

Open:
- `http://localhost:8000/static/index.html` for the Users page.
- `http://localhost:8000/static/planning.html` for the Planning page.

### Local (Python)
```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open:
- `http://localhost:8000/static/index.html` for the Users page.
- `http://localhost:8000/static/planning.html` for the Planning page.

## Documentation
See [`docs/DOCUMENTATION.md`](docs/DOCUMENTATION.md) for full functional specs and setup details.

## Development
Install optional dev dependencies from `pyproject.toml` to run tests and linters:
```bash
uv pip install -e ".[dev]"
pytest
```
