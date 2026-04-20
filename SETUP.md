# Career OS — Setup Guide

## Quick Start (Local)

### Prerequisites
- Python 3.12+
- pip

### 1. Backend Setup
```bash
cd Backend
pip install -r requirements.txt
cp .env.example .env          # Edit .env with your API keys
python -m uvicorn app.main:app --reload --port 8000
```
Backend runs at: http://localhost:8000
API Docs at: http://localhost:8000/docs

### 2. Frontend Setup
```bash
cd Frontend
python serve.py
```
Frontend runs at: http://localhost:5500

---

## Docker Setup (One Command)

```bash
cp Backend/.env.example Backend/.env   # Edit with your API keys
docker-compose up --build
```
- Frontend: http://localhost:5500
- Backend: http://localhost:8000

---

## API Keys (Optional — features degrade gracefully without them)

| Key | Feature | Get it at |
|-----|---------|-----------|
| `GEMINI_API_KEY` | AI narrative suggestions (Feature 5) | https://aistudio.google.com |
| `ASSEMBLYAI_API_KEY` | Audio transcription (Feature 2) | https://www.assemblyai.com |
| `ADZUNA_APP_ID/KEY` | Live job market data (Feature 3) | https://developer.adzuna.com |
| `REED_API_KEY` | Additional job data (Feature 3) | https://www.reed.co.uk/developers |

---

## Running Tests
```bash
cd Backend
pip install pytest
pytest tests/ -v
```

---

## SQLite → PostgreSQL Migration

The app uses SQLite by default. To switch to PostgreSQL:

1. Install psycopg2: `pip install psycopg2-binary`
2. Set in `.env`: `DATABASE_URL=postgresql://user:password@localhost:5432/career_os`
3. Run migrations: `python -m alembic upgrade head` (or re-run the app — SQLModel auto-creates tables)

The API contracts don't change — only the `DATABASE_URL` env var needs updating.

---

## CI Pipeline (GitHub Actions)

To enable automated testing on push, add a GitHub token with `workflow` scope, then push `.github/workflows/ci.yml`:

```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r Backend/requirements.txt
      - run: pytest Backend/tests/ -v
```
