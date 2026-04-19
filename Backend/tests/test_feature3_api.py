from fastapi.testclient import TestClient

from app.db import create_db_and_tables
from app.main import app

create_db_and_tables()
client = TestClient(app)


def test_feature3_full_api_flow():
    market_response = client.post(
        "/api/feature3/market-snapshot",
        json={
            "candidate_id": "candidate-f3",
            "target_role": "Fullstack Engineer",
            "region": "PK",
            "remote_only": True,
            "search_terms": ["react", "python", "sql"],
        },
    )
    assert market_response.status_code == 200
    market = market_response.json()
    assert market["snapshot_id"] > 0
    assert "demand_supply_ratio" in market

    gap_response = client.post(
        "/api/feature3/gap-analysis",
        json={
            "candidate_id": "candidate-f3",
            "market_snapshot_id": market["snapshot_id"],
            "current_skills": ["react", "javascript", "python"],
            "years_experience": 2.0,
            "github_username": "",
        },
    )
    assert gap_response.status_code == 200
    gap = gap_response.json()
    assert gap["gap_snapshot_id"] > 0
    assert "roadmap_to_90" in gap

    sprint_response = client.post(
        "/api/feature3/sprint",
        json={
            "candidate_id": "candidate-f3",
            "gap_snapshot_id": gap["gap_snapshot_id"],
            "target_role": "Fullstack Engineer",
            "primary_skill": "kubernetes",
        },
    )
    assert sprint_response.status_code == 200
    sprint = sprint_response.json()
    assert sprint["sprint_id"] > 0

    quiz_response = client.post(
        f"/api/feature3/sprint/{sprint['sprint_id']}/quiz",
        json={
            "answers": [
                "Trade-off is reliability and latency with measurable metrics.",
                "Failure mode is stale cache; mitigate with constraints and tests.",
                "Result improved by 15 percent with clear impact.",
            ]
        },
    )
    assert quiz_response.status_code == 200
    assert "score" in quiz_response.json()

    inject_response = client.post(
        f"/api/feature3/sprint/{sprint['sprint_id']}/resume-inject",
        json={
            "project_name": "Skill Sprint API",
            "baseline_context": "a tight deadline project",
            "impact_metric_hint": "p95 latency",
        },
    )
    assert inject_response.status_code == 200
    assert len(inject_response.json()["star_bullets"]) > 0

    future_response = client.post(
        "/api/feature3/future-insights",
        json={
            "candidate_id": "candidate-f3",
            "market_snapshot_id": market["snapshot_id"],
            "current_skills": ["python", "llm", "agents", "testing"],
        },
    )
    assert future_response.status_code == 200
    assert future_response.json()["insight_id"] > 0

    roi_response = client.post(
        "/api/feature3/roi-report",
        json={
            "candidate_id": "candidate-f3",
            "market_snapshot_id": market["snapshot_id"],
            "gap_snapshot_id": gap["gap_snapshot_id"],
            "current_salary_usd": 10000,
            "target_path": "fullstack",
        },
    )
    assert roi_response.status_code == 200
    assert roi_response.json()["report_id"] > 0

    history_response = client.get("/api/feature3/candidate/candidate-f3/historical-gaps")
    assert history_response.status_code == 200
    assert "monthly_snapshots" in history_response.json()
