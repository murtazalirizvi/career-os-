from fastapi.testclient import TestClient

from app.db import create_db_and_tables
from app.main import app

create_db_and_tables()
client = TestClient(app)


def test_feature5_api_session_and_export_flow():
    create = client.post(
        "/api/feature5/sessions",
        json={
            "candidate_id": "candidate-f5",
            "repo_subpath": ".",
            "target_role": "Software Engineer",
            "tone": "business",
            "jd_text": "backend fastapi testing system design",
            "resume_text": "Built backend APIs and analytics engines",
            "linkedin_text": "Built product systems with measurable impact",
            "github_repo": "",
            "selected_projects": ["Backend", "Frontend", "Requirements"],
        },
    )
    assert create.status_code == 200
    session_data = create.json()
    sid = session_data["session_id"]

    get_one = client.get(f"/api/feature5/sessions/{sid}")
    assert get_one.status_code == 200
    assert "epic_5_1" in get_one.json()["deep_analysis"]

    consistency = client.post(
        f"/api/feature5/sessions/{sid}/consistency-check",
        json={
            "resume_text": "FastAPI backend testing and feature delivery",
            "linkedin_text": "Built narrative analytics product",
        },
    )
    assert consistency.status_code == 200
    assert "consistency_score" in consistency.json()["consistency_check"]

    export = client.post(
        f"/api/feature5/sessions/{sid}/export",
        json={"include_sections": ["linkedin_sync", "resume_optimizer", "case_study_pdf"]},
    )
    assert export.status_code == 200
    assert "markdown_bundle" in export.json()

    case_pdf = client.get(f"/api/feature5/sessions/{sid}/case-study.pdf")
    assert case_pdf.status_code == 200
    assert case_pdf.headers.get("content-type", "").startswith("application/pdf")

    site_zip = client.get(f"/api/feature5/sessions/{sid}/portfolio-site")
    assert site_zip.status_code == 200
    assert site_zip.headers.get("content-type", "").startswith("application/zip")

    history = client.get("/api/feature5/candidate/candidate-f5/sessions")
    assert history.status_code == 200
    assert len(history.json()["sessions"]) >= 1
