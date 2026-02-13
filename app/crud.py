from sqlalchemy.orm import Session
from datetime import datetime
from .models import User, Job, JobStatus, Role
from .security import hash_password, verify_password

def create_user(db: Session, username: str, password: str, role: str, quota_hours: float) -> User:
    try:
        role_enum = Role(role)
    except ValueError:
        raise ValueError(f"Invalid role: {role}. Must be 'admin' or 'user'")
    
    u = User(username=username, password_hash=hash_password(password), role=role_enum, quota_hours=quota_hours)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

def authenticate(db: Session, username: str, password: str) -> User | None:
    u = db.query(User).filter(User.username == username).first()
    if not u:
        return None
    if not verify_password(password, u.password_hash):
        return None
    return u

def create_job(db: Session, owner: User, payload: dict) -> Job:
    need = float(payload["est_hours"]) * int(payload["gpu_count"])
    if owner.quota_hours < need:
        raise ValueError(f"Not enough quota. Need {need}, have {owner.quota_hours}")

    job = Job(
        owner_id=owner.id,
        gpu_type=payload["gpu_type"],
        gpu_count=payload["gpu_count"],
        est_hours=payload["est_hours"],
        command=payload["command"],
        sensitive=payload["sensitive"],
        data_path=payload["data_path"],
        status=JobStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    job.append_log("Job submitted (waiting for admin approval).")
    db.add(job)
    db.commit()
    db.refresh(job)
    return job

def set_status(db: Session, job: Job, status: JobStatus, msg: str):
    job.status = status
    job.updated_at = datetime.utcnow()
    job.append_log(msg)
    db.commit()
    db.refresh(job)
    return job

def deduct_quota(db: Session, owner: User, job: Job):
    used = float(job.est_hours) * int(job.gpu_count)
    owner.quota_hours = max(0.0, owner.quota_hours - used)
    db.commit()
    db.refresh(owner)
