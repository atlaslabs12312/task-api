# Task API

A small production-style REST API built with Python and FastAPI.

## Features

- Health check endpoint
- Task creation, listing, lookup, and completion
- Request validation with Pydantic
- SQL database persistence with SQLAlchemy
- SQLite by default for local development
- PostgreSQL support through `DATABASE_URL`
- Automated API tests with pytest
- GitHub Actions CI on every push and pull request

## API

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | /health | Health check |
| POST | /tasks | Create a task |
| GET | /tasks | List tasks |
| GET | /tasks/{task_id} | Get a task |
| PATCH | /tasks/{task_id}/complete | Mark a task complete |

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the interactive API documentation at `/docs`.

## Test

```bash
pytest -q
```

## PostgreSQL

Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL, for example:

```
postgresql+psycopg://user:password@localhost:5432/task_api
```
