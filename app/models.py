import enum
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .db import Base

class Role(str, enum.Enum):
    admin = "admin"
    user = "user"

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.user)
    quota_hours: Mapped[float] = mapped_column(Float, default=10.0)

    jobs = relationship("Job", back_populates="owner")

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    gpu_type: Mapped[str] = mapped_column(String(50), default="T4")
    gpu_count: Mapped[int] = mapped_column(Integer, default=1)
    est_hours: Mapped[float] = mapped_column(Float, default=1.0)
    command: Mapped[str] = mapped_column(Text, default="echo hello")
    sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    data_path: Mapped[str] = mapped_column(String(200), default="")

    status: Mapped[JobStatus] = mapped_column(Enum(JobStatus), default=JobStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    log: Mapped[str] = mapped_column(Text, default="")

    owner = relationship("User", back_populates="jobs")

    def append_log(self, msg: str):
        self.log = (self.log or "") + f"[{datetime.utcnow().isoformat()}] {msg}\n"
