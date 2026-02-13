# GPU as a Service (Simulation) — Simple Version

This project implements a **GPU-as-a-Service** web API in **simulation mode** (no real GPU execution). It supports:
- Users & Admin roles (JWT authentication)
- Submit jobs with metadata
- Admin approval required before execution
- Basic quota (GPU-hours) check
- Job lifecycle: **PENDING → APPROVED → RUNNING → COMPLETED/FAILED**

## 1) Quick Run (without Docker)
### Prerequisites
- Python 3.10+

### Install
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate
pip install -r requirements.txt
```

### Start API
```bash
uvicorn app.main:app --reload
```

Open Swagger UI:
- http://127.0.0.1:8000/docs

## 2) Demo Flow (Swagger)
1. Register admin:
   - POST `/auth/register` with `role="admin"` and e.g. `quota_hours=999`
2. Register a normal user:
   - POST `/auth/register` with `role="user"` and e.g. `quota_hours=10`
3. Login as user:
   - POST `/auth/login` → copy the `access_token`
4. Submit job as user:
   - POST `/jobs` (Authorization: Bearer TOKEN)
5. Login as admin and approve:
   - POST `/admin/jobs/{job_id}/approve`
6. Watch job status:
   - GET `/jobs/{job_id}`

A background simulator runs approved jobs automatically.

## 3) Run with Docker Compose
```bash
docker compose up --build
```

## 4) Tests
```bash
pytest -q
```
