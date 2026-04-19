from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from app.db import create_db_and_tables
from app.main import app

create_db_and_tables()
client = TestClient(app)


def test_metrics_ingest_and_kpi_dashboard():
    uid = f"candidate-metrics-{int(datetime.now(timezone.utc).timestamp())}"
    sid = "session-analytics-1"
    now = datetime.now(timezone.utc)

    payload = [
        {
            "event_name": "user_signed_up",
            "event_version": "1.0",
            "occurred_at_utc": now.isoformat(),
            "user_id": uid,
            "session_id": sid,
            "platform": "web",
            "feature_area": "onboarding",
            "metadata_json": {},
        },
        {
            "event_name": "first_analysis_completed",
            "event_version": "1.0",
            "occurred_at_utc": (now + timedelta(minutes=2)).isoformat(),
            "user_id": uid,
            "session_id": sid,
            "platform": "web",
            "feature_area": "feature1",
            "metadata_json": {"processing_latency_ms": 1200},
        },
        {
            "event_name": "recommendation_viewed",
            "event_version": "1.0",
            "occurred_at_utc": (now + timedelta(minutes=3)).isoformat(),
            "user_id": uid,
            "session_id": sid,
            "platform": "web",
            "feature_area": "feature1",
            "metadata_json": {},
        },
        {
            "event_name": "recommendation_applied",
            "event_version": "1.0",
            "occurred_at_utc": (now + timedelta(minutes=4)).isoformat(),
            "user_id": uid,
            "session_id": sid,
            "platform": "web",
            "feature_area": "feature1",
            "metadata_json": {},
        },
        {
            "event_name": "application_logged",
            "event_version": "1.0",
            "occurred_at_utc": (now + timedelta(days=1)).isoformat(),
            "user_id": uid,
            "session_id": sid,
            "platform": "web",
            "feature_area": "applications",
            "application_id": "app-100",
            "metadata_json": {"company_name_normalized": "acme"},
        },
        {
            "event_name": "invitation_received",
            "event_version": "1.0",
            "occurred_at_utc": (now + timedelta(days=3)).isoformat(),
            "user_id": uid,
            "session_id": sid,
            "platform": "web",
            "feature_area": "applications",
            "application_id": "app-100",
            "metadata_json": {},
        },
        {
            "event_name": "project_selected_for_narrative",
            "event_version": "1.0",
            "occurred_at_utc": (now + timedelta(minutes=6)).isoformat(),
            "user_id": uid,
            "session_id": sid,
            "platform": "web",
            "feature_area": "feature5",
            "project_id": "backend",
            "metadata_json": {},
        },
        {
            "event_name": "star_bullets_generated",
            "event_version": "1.0",
            "occurred_at_utc": (now + timedelta(minutes=7)).isoformat(),
            "user_id": uid,
            "session_id": sid,
            "platform": "web",
            "feature_area": "feature5",
            "project_id": "backend",
            "metadata_json": {},
        },
    ]

    ingest = client.post("/api/metrics/events", json=payload)
    assert ingest.status_code == 200
    assert ingest.json()["accepted"] == len(payload)

    kpis = client.get(f"/api/metrics/kpis?user_id={uid}&window_days=28")
    assert kpis.status_code == 200
    data = kpis.json()
    assert data["interview_invitation_rate"] == 1.0
    assert data["activation_rate"] == 1.0
    assert data["recommendation_adoption_rate"] == 1.0
    assert data["narrative_coverage"] == 1.0
    assert data["time_to_first_invitation_days"] is not None

    dashboard = client.get(f"/api/metrics/dashboard?user_id={uid}&window_days=28")
    assert dashboard.status_code == 200
    d = dashboard.json()
    assert "kpi_panel" in d
    assert "funnel_panel" in d
    assert "feature_impact_panel" in d
    assert "reliability_panel" in d


def test_application_log_and_status_updates_emit_metrics_events():
    uid = f"candidate-app-{int(datetime.now(timezone.utc).timestamp())}"
    app_id = "app-200"

    create = client.post(
        "/api/metrics/applications",
        json={
            "user_id": uid,
            "application_id": app_id,
            "company_name_normalized": "globex",
            "role_name_normalized": "backend_engineer",
            "channel": "job_board",
        },
    )
    assert create.status_code == 200
    assert create.json()["application_id"] == app_id

    update = client.patch(
        f"/api/metrics/applications/{app_id}?user_id={uid}",
        json={"status": "invited", "status_reason": "screening scheduled"},
    )
    assert update.status_code == 200
    assert update.json()["status"] == "invited"

    rows = client.get(f"/api/metrics/applications/{uid}")
    assert rows.status_code == 200
    assert len(rows.json()) >= 1

    kpis = client.get(f"/api/metrics/kpis?user_id={uid}&window_days=28")
    assert kpis.status_code == 200
    assert kpis.json()["counts"]["applications"] >= 1

    exported = client.get(f"/api/metrics/users/{uid}/export")
    assert exported.status_code == 200
    export_payload = exported.json()
    assert export_payload["user_id"] == uid
    assert isinstance(export_payload["events"], list)
    assert isinstance(export_payload["applications"], list)

    deleted = client.delete(f"/api/metrics/users/{uid}")
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] is True
