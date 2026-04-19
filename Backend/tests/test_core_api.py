from fastapi.testclient import TestClient

from app.db import create_db_and_tables
from app.main import app

create_db_and_tables()
client = TestClient(app)


def test_core_daily_plan_returns_actionable_payload():
    candidate_id = "candidate-core"

    response = client.get(f"/api/core/daily-plan/{candidate_id}")
    assert response.status_code == 200
    payload = response.json()

    assert payload["candidate_id"] == candidate_id
    assert "readiness_score" in payload
    assert "confidence_label" in payload
    assert isinstance(payload["next_actions"], list)
    assert isinstance(payload["metrics_snapshot"], dict)
