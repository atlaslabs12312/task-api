# Task API

A portfolio-grade REST API built with **Python, FastAPI, SQLAlchemy, PostgreSQL/SQLite, pytest, and GitHub Actions**.

The project demonstrates the backend fundamentals commonly requested for junior API work: database persistence, REST design, validation, filtering, basic role-based authorization, audit logging, automated tests, and API documentation.

## Features

- FastAPI REST API with OpenAPI/Swagger at `/docs`
- SQLAlchemy persistence
- SQLite by default for local development
- PostgreSQL support through `DATABASE_URL`
- Pydantic request/response validation
- Task CRUD-style operations plus completion workflow
- Search/filtering with `GET /tasks?q=...`
- Basic role-based access control:
  - `viewer`: read task data
  - `editor`: create and complete tasks
  - `admin`: access audit logs
- Audit logging for task reads, listings, creation, and completion
- Pytest API test coverage for success, validation/permissions, filtering, and errors
- GitHub Actions CI on every push and pull request

> **Security note:** the `X-Role` header is intentionally a simple portfolio/demo authorization mechanism. It is not production authentication. A real deployment should replace it with authenticated users and signed credentials/tokens.

## API

| Method | Endpoint | Access | Description |
| --- | --- | --- | --- |
| GET | `/health` | Public | Health check |
| POST | `/tasks` | Editor/Admin | Create a task |
| GET | `/tasks` | Any role | List and optionally filter tasks |
| GET | `/tasks/{task_id}` | Any role | Get one task |
| PATCH | `/tasks/{task_id}/complete` | Editor/Admin | Mark a task complete |
| GET | `/audit-logs` | Admin | Review audit events |

Example filtering request:

```text
GET /tasks?q=API
X-Role: viewer
```

## Local setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/health`

## Run tests

```bash
pytest -q
```

## PostgreSQL

Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL:

```text
postgresql+psycopg://user:password@localhost:5432/task_api
```

The same application code can then use PostgreSQL instead of the default local SQLite database.

## CI

GitHub Actions installs the dependency set and runs `pytest -q` for pushes and pull requests.

## Project structure

```text
task-api/
├── .github/workflows/tests.yml
├── app/main.py
├── tests/test_api.py
├── requirements.txt
└── README.md
```

## Portfolio focus

This repository is intentionally small enough to understand and hand off, while demonstrating:

1. API contract design
2. Relational persistence
3. Validation and HTTP error handling
4. Basic authorization
5. Auditability
6. Automated testing
7. PostgreSQL compatibility
8. Git-based CI workflow
