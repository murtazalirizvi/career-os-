from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.db import create_db_and_tables, engine as db_engine
from app.main import app
from app.models import (
    Feature1Analysis,
    Feature2InterviewAutopsy,
    Feature3GapSnapshot,
    Feature3MarketSnapshot,
    UserAccount,
)
from app.models_jobs import Job, JobStatus

create_db_and_tables()
client = TestClient(app)


def _register_user(candidate_suffix: str) -> tuple[str, str]:
    email = f"dashboard-{candidate_suffix}@example.com"
    candidate_id = f"candidate-dashboard-{candidate_suffix}"
    password = "StrongPass#123"
    response = client.post(
        "/api/auth/register",
        json={
            "candidate_id": candidate_id,
            "email": email,
            "full_name": "Dashboard User",
            "password": password,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    return payload["session"]["access_token"], payload["user"]["candidate_id"]


def _seed_dashboard_data(candidate_id: str) -> None:
    with Session(db_engine) as session:
        user = session.exec(
            select(UserAccount).where(UserAccount.candidate_id == candidate_id)
        ).first()
        assert user is not None

        feature1 = Feature1Analysis(
            candidate_id=candidate_id,
            job_category="frontend",
            resume_filename="resume.pdf",
            resume_path="/tmp/resume.pdf",
            version_number=1,
            overall_score=84.0,
            visual_score=82.0,
            ats_score=88.0,
            semantic_score=79.0,
            benchmark_score=81.0,
            eye_tracking_summary="Strong visual flow.",
            ats_summary="ATS parser friendly.",
            semantic_summary="Good keyword alignment.",
            benchmark_summary="Above average benchmark fit.",
            hotzones_json="[]",
            metrics_json='{"confidence_tier_distribution": {"high": 2}}',
            recommendations_json='["Tighten impact bullets"]',
            ai_recommendations_json='["Add stronger metrics"]',
            raw_resume_text="Resume text",
        )
        session.add(feature1)
        session.commit()
        session.refresh(feature1)

        market = Feature3MarketSnapshot(
            candidate_id=candidate_id,
            target_role="Frontend Engineer",
            region="US",
            remote_only=True,
            jobs_json="[]",
            clustering_json="{}",
            demand_supply_json="{}",
            salary_map_json="{}",
            remote_market_json="{}",
            source_meta_json="{}",
        )
        session.add(market)
        session.commit()
        session.refresh(market)

        gap = Feature3GapSnapshot(
            market_snapshot_id=market.id,
            candidate_id=candidate_id,
            current_skills_json='["react", "typescript"]',
            target_skills_json='["react", "typescript", "testing"]',
            radar_chart_json="{}",
            roadmap_json="{}",
            niche_recommendations_json="[]",
            github_validation_json="{}",
            historical_gap_json="{}",
            match_score=72.0,
            gap_to_top10_score=18.0,
        )
        session.add(gap)
        session.commit()
        session.refresh(gap)

        interview = Feature2InterviewAutopsy(
            candidate_id=candidate_id,
            company_name="Acme",
            role_name="Frontend Engineer",
            interview_round="onsite",
            lifecycle_stage="interview",
            challenge_question="Tell me about a bug you fixed.",
            interview_outcome="rejected",
            rejection_reason_hint="Needs clearer trade-off communication.",
            advanced_round_reached=False,
            ingestion_json="{}",
            technical_json="{}",
            behavioral_json="{}",
            strategic_actions_json="{}",
            analytics_snapshot_json="{}",
            score_json='{"overall_autopsy_score": 76.0, "technical_accuracy": 81.0, "behavioral_quality": 73.0, "strategic_recovery_readiness": 68.0}',
        )
        session.add(interview)
        session.add(
            Job(
                owner_id=user.id,
                company="Acme",
                position="Frontend Engineer",
                status=JobStatus.applied,
            )
        )
        session.commit()


def test_me_dashboard_returns_partial_payload_when_only_resume_exists():
    token, candidate_id = _register_user("partial")

    with Session(db_engine) as session:
        feature1 = Feature1Analysis(
            candidate_id=candidate_id,
            job_category="backend",
            resume_filename="resume.pdf",
            resume_path="/tmp/resume.pdf",
            version_number=1,
            overall_score=90.0,
            visual_score=88.0,
            ats_score=91.0,
            semantic_score=87.0,
            benchmark_score=89.0,
            eye_tracking_summary="Clean resume layout.",
            ats_summary="ATS ready.",
            semantic_summary="Strong semantic alignment.",
            benchmark_summary="High benchmark fit.",
            hotzones_json="[]",
            metrics_json="{}",
            recommendations_json="[]",
            ai_recommendations_json="[]",
            raw_resume_text="Resume text",
        )
        session.add(feature1)
        session.commit()

    response = client.get(
        "/api/me/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()

    assert payload["readiness_score"] == 90.0
    assert payload["readiness"]["label"] == "Ready to Apply"
    assert payload["latest_analysis"]["analysis_id"] is not None
    assert payload["interview_analysis"]["interview_id"] is None
    assert payload["market_analysis"]["gap_snapshot_id"] is None
    assert payload["status_indicators"]["resume_ready"] is True
    assert payload["status_indicators"]["interview_ready"] is False
    assert payload["status_indicators"]["market_ready"] is False


def test_me_dashboard_combines_all_scores_with_normalized_weights():
    token, candidate_id = _register_user("full")
    _seed_dashboard_data(candidate_id)

    response = client.get(
        "/api/me/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()

    expected = round(((84.0 * 0.5) + (76.0 * 0.3) + (72.0 * 0.2)) / (0.5 + 0.3 + 0.2), 2)
    assert payload["readiness_score"] == expected
    assert payload["readiness"]["label"] == "Strong Candidate"
    assert payload["latest_analysis"]["score_breakdown"]["ats_integrity"] == 88.0
    assert payload["interview_analysis"]["overall_score"] == 76.0
    assert payload["interview_analysis"]["score_breakdown"]["technical_accuracy"] == 81.0
    assert payload["market_analysis"]["match_score"] == 72.0
    assert len(payload["analytics"]["chart_data"]) > 0
    assert payload["job_pipeline"]["Applied"] == 1
