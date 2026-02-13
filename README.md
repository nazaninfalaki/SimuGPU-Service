# GPU Job Service (Simulation)

This project is a simple backend service that simulates how a GPU job scheduling system works.

I built this project to practice backend concepts like authentication, role-based access control, and background job processing using FastAPI.

Instead of using a real GPU, jobs are simulated and automatically completed after approval.

---

## What this project does

There are two types of users:

### User

* Can register and login
* Can submit a job
* Can check job status

### Admin

* Can approve submitted jobs
* Approved jobs run automatically in the background

Job lifecycle:
PENDING → APPROVED → RUNNING → COMPLETED

---

## Technologies Used

* Python
* FastAPI
* JWT Authentication
* SQLite
* Background Tasks
* Docker (optional)

---

## How to Run (without Docker)

### 1) Create virtual environment

```bash
python -m venv .venv
```

### Activate environment

Windows:

```bash
.venv\Scripts\activate
```

Linux/Mac:

```bash
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Run the server

```bash
uvicorn app.main:app --reload
```

Open browser:

```
http://127.0.0.1:8000/docs
```

---

## Example Flow

1. Register admin
2. Register normal user
3. Login as user
4. Submit job
5. Login as admin and approve job
6. Watch job become completed automatically

---

## Run with Docker

```bash
docker compose up --build
```

---

## Goal of the Project

The purpose of this project is learning how job scheduling services work in backend systems such as AI platforms or cloud GPU providers.

This is only a simulation project for educational use.
