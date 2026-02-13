from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_quota_blocks_job():
    # register user with very small quota
    r = client.post("/auth/register", json={"username":"u1","password":"pass","role":"user","quota_hours":1})
    assert r.status_code == 200

    # login
    r = client.post("/auth/login", json={"username":"u1","password":"pass"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    # submit job needing >1 quota (est_hours*gpu_count = 2*1 = 2)
    r = client.post("/jobs",
        json={"gpu_type":"T4","gpu_count":1,"est_hours":2,"command":"echo hi","sensitive":False,"data_path":""},
        headers={"Authorization": f"Bearer {token}"}    
    )
    assert r.status_code == 400
