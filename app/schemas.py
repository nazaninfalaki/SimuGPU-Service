from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal

class RegisterIn(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=4, max_length=100)
    role: Literal["admin", "user"] = "user"
    quota_hours: float = Field(default=10.0, ge=0)

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginIn(BaseModel):
    username: str
    password: str

class JobCreateIn(BaseModel):
    gpu_type: str = "T4"
    gpu_count: int = Field(default=1, ge=1, le=8)
    est_hours: float = Field(default=1.0, gt=0)
    command: str = "echo hello"
    sensitive: bool = False
    data_path: str = ""

class JobOut(BaseModel):
    id: int
    owner: str
    gpu_type: str
    gpu_count: int
    est_hours: float
    command: str
    sensitive: bool
    data_path: str
    status: str
    created_at: datetime
    updated_at: datetime
    log: str

    class Config:
        from_attributes = True
