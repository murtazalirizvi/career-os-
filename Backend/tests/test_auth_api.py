from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.db import create_db_and_tables
from app.main import app

create_db_and_tables()
client = TestClient(app)


def test_register_login_me_logout_flow():
    suffix = int(datetime.now(timezone.utc).timestamp())
    candidate_id = f"candidate-auth-{suffix}"
    email = f"auth{suffix}@example.com"
    password = "StrongPass#123"

    register = client.post(
        "/api/auth/register",
        json={
            "candidate_id": candidate_id,
            "email": email,
            "full_name": "Auth User",
            "password": password,
        },
    )
    assert register.status_code == 200
    reg_payload = register.json()
    token = reg_payload["session"]["access_token"]
    assert reg_payload["user"]["candidate_id"] == candidate_id

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["user"]["email"] == email

    logout = client.post("/api/auth/logout", json={"access_token": token})
    assert logout.status_code == 200
    assert logout.json()["ok"] is True

    me_after_logout = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_after_logout.status_code == 401

    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert login.status_code == 200
    assert login.json()["session"]["access_token"]
