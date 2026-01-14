# TeamPlanner

TeamPlanner is a lightweight web app for planning smart-working days and days off within a small team.

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
