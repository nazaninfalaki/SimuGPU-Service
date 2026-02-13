from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import threading

from .db import Base, engine, SessionLocal, get_db
from . import schemas, crud
from .models import User, Job, JobStatus
from .security import create_access_token
from .deps import get_current_user, require_admin
from .simulator import worker_loop
from .crud import set_status

app = FastAPI(
    title="GPU as a Service (Simulation)",
    swagger_ui_init_oauth=None
)

Base.metadata.create_all(bind=engine)

_stop = {"stop": False}
_thread = None

@app.on_event("startup")
def start_worker():
    global _thread
    if _thread is None:
        _thread = threading.Thread(target=worker_loop, args=(SessionLocal, _stop), daemon=True)
        _thread.start()

@app.on_event("shutdown")
def stop_worker():
    _stop["stop"] = True

@app.post("/auth/register")
def register(payload: schemas.RegisterIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == payload.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    try:
        u = crud.create_user(db, payload.username, payload.password, payload.role, payload.quota_hours)
        return {"id": u.id, "username": u.username, "role": u.role.value, "quota_hours": u.quota_hours}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@app.post("/auth/login", response_model=schemas.TokenOut)
def login(payload: schemas.LoginIn, db: Session = Depends(get_db)):
    u = crud.authenticate(db, payload.username, payload.password)
    if not u:
        raise HTTPException(status_code=401, detail="Invalid username/password")
    token = create_access_token(sub=u.username, role=u.role.value)
    return schemas.TokenOut(access_token=token)

@app.post("/jobs", response_model=schemas.JobOut)
def submit_job(payload: schemas.JobCreateIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    try:
        job = crud.create_job(db, user, payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return schemas.JobOut(
        id=job.id,
        owner=user.username,
        gpu_type=job.gpu_type,
        gpu_count=job.gpu_count,
        est_hours=job.est_hours,
        command=job.command,
        sensitive=job.sensitive,
        data_path=job.data_path,
        status=job.status.value,
        created_at=job.created_at,
        updated_at=job.updated_at,
        log=job.log,
    )

@app.get("/jobs", response_model=List[schemas.JobOut])
def list_my_jobs(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    jobs = db.query(Job).filter(Job.owner_id == user.id).order_by(Job.created_at.desc()).all()
    out = []
    for j in jobs:
        out.append(schemas.JobOut(
            id=j.id,
            owner=user.username,
            gpu_type=j.gpu_type,
            gpu_count=j.gpu_count,
            est_hours=j.est_hours,
            command=j.command,
            sensitive=j.sensitive,
            data_path=j.data_path,
            status=j.status.value,
            created_at=j.created_at,
            updated_at=j.updated_at,
            log=j.log,
        ))
    return out

@app.get("/jobs/{job_id}", response_model=schemas.JobOut)
def get_job(job_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    job = db.query(Job).filter(Job.id == job_id, Job.owner_id == user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return schemas.JobOut(
        id=job.id,
        owner=user.username,
        gpu_type=job.gpu_type,
        gpu_count=job.gpu_count,
        est_hours=job.est_hours,
        command=job.command,
        sensitive=job.sensitive,
        data_path=job.data_path,
        status=job.status.value,
        created_at=job.created_at,
        updated_at=job.updated_at,
        log=job.log,
    )

@app.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"username": user.username, "role": user.role.value, "quota_hours": user.quota_hours}

@app.get("/admin/jobs")
def admin_list_jobs(db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    jobs = db.query(Job).order_by(Job.created_at.desc()).all()
    return [{
        "id": j.id,
        "owner_id": j.owner_id,
        "gpu_type": j.gpu_type,
        "gpu_count": j.gpu_count,
        "est_hours": j.est_hours,
        "status": j.status.value,
        "created_at": j.created_at,
        "updated_at": j.updated_at,
        "sensitive": j.sensitive,
    } for j in jobs]

@app.post("/admin/jobs/{job_id}/approve")
def approve_job(job_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only PENDING jobs can be approved")
    set_status(db, job, JobStatus.APPROVED, f"Approved by admin {admin.username}.")
    return {"ok": True, "job_id": job_id, "status": job.status.value}

@app.post("/admin/jobs/{job_id}/reject")
def reject_job(job_id: int, db: Session = Depends(get_db), admin: User = Depends(require_admin)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != JobStatus.PENDING:
        raise HTTPException(status_code=400, detail="Only PENDING jobs can be rejected")
    set_status(db, job, JobStatus.REJECTED, f"Rejected by admin {admin.username}.")
    return {"ok": True, "job_id": job_id, "status": job.status.value}
