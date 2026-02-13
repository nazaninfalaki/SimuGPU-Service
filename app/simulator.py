import time
from sqlalchemy.orm import Session
from .models import Job, JobStatus, User
from .crud import set_status, deduct_quota
from .config import SIM_SPEED

def run_one_job(db: Session, job: Job):
    set_status(db, job, JobStatus.RUNNING, "Job started (simulated GPU execution).")
    seconds = max(1.0, float(job.est_hours) * int(job.gpu_count) * SIM_SPEED)
    time.sleep(seconds)
    set_status(db, job, JobStatus.COMPLETED, f"Job completed. Simulated runtime {seconds:.1f}s.")
    owner = db.query(User).filter(User.id == job.owner_id).first()
    if owner:
        deduct_quota(db, owner, job)

def worker_loop(db_factory, stop_flag):
    while not stop_flag["stop"]:
        db = db_factory()
        try:
            job = (
                db.query(Job)
                .filter(Job.status == JobStatus.APPROVED)
                .order_by(Job.created_at.asc())
                .first()
            )
            if job:
                run_one_job(db, job)
            else:
                time.sleep(1.0)
        finally:
            db.close()
