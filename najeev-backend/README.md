# Najeev Notes backend

FastAPI backend with PostgreSQL admin/note storage and MongoDB audit events. All note and audit endpoints require an admin bearer token. Admins only access their own notes. The seed command creates 20 sample notes.

## Run locally (PowerShell, Python 3.12+ and Docker)

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
# Set JWT_SECRET and ADMIN_PASSWORD in .env before continuing.
docker compose up -d
# Wait for both databases to accept connections.
.venv\Scripts\python -m app.seed
.venv\Scripts\python -m uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs and use Authorize with the admin credentials from `.env`. Login is `POST /auth/token` with form fields `username` and `password`. No public admin registration exists. Rerunning the seed does not reset an existing admin password or duplicate existing sample titles.

After Docker Desktop is running and `.env` is configured, `powershell -ExecutionPolicy Bypass -File .\start.ps1` automates environment setup, container startup, database readiness checks, seeding, and serving the API. Windows may require a restart after installing Docker/WSL and enabling Virtual Machine Platform.

## Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| POST | /auth/token | Admin login, 30-minute JWT |
| GET | /health | Check PostgreSQL and MongoDB |
| GET | /notes | Paginated own notes (`offset`, `limit`) |
| POST | /notes | Create note (`title`, `content`) |
| GET | /notes/{id} | Read own note |
| PUT | /notes/{id} | Replace title and content |
| DELETE | /notes/{id} | Delete own note |
| GET | /audit | Recent own MongoDB audit events |

## MVC layout

- `app/models.py`: SQLAlchemy persistence models.
- `app/views.py`: Pydantic JSON request/response views.
- `app/controllers.py`: HTTP controllers.
- `app/services.py`: audit operations; `security.py`: authentication.
- `app/seed.py`: explicit database initialization and sample data.

## Validation and operational limits

Run `.venv\Scripts\python -m pytest -q`. API tests use SQLite and mocked MongoDB; real database connectivity must also be checked with `/health` after local startup. The compose credentials are local development values. Use managed secrets, HTTPS and login rate limiting before public deployment. Database schema creation is for initial setup; use migrations for future schema changes. MongoDB audit writes are best effort: failures are logged, but committed PostgreSQL changes still succeed. This is not a guaranteed delivery audit system.

The screenshot's `Saas-catpad.vercel.app` text is treated as a reference name, not a deployment destination. This project is backend only; no deployment is performed.

Authentication follows the [FastAPI JWT guide](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/). MongoDB uses the [official PyMongo driver](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/connect/mongoclient/).
