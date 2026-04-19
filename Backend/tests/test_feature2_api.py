from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_feature2_quick_debrief_api():
    response = client.post(
        "/api/feature2/quick-debrief",
        json={"debrief_text": "I froze and then gave too short answers about API design?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "extracted_hardest_question" in payload
    assert "immediate_next_actions" in payload


def test_feature2_interview_create_and_fetch():
    create_response = client.post(
        "/api/feature2/interviews",
        json={
            "candidate_id": "candidate-test",
            "interview_round": "tech",
            "company_name": "Acme",
            "role_name": "Backend Engineer",
            "interview_notes": "I struggled with API versioning and SQL indexes.",
            "transcript_text": "Interviewer: How would you version your API? Candidate: I would use v1 routes.",
            "assembly_audio_url": "",
            "use_assemblyai": False,
            "culture_vibe": "neutral",
            "interviewer_friendliness": 7,
            "lifecycle_stage": "tech",
            "technical_expectations": ["api", "sql"],
            "interview_outcome": "rejected",
            "rejection_reason_hint": "technical depth",
            "advanced_round_reached": False,
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()
    interview_id = created["interview_id"]

    get_response = client.get(f"/api/feature2/interviews/{interview_id}")
    assert get_response.status_code == 200
    fetched = get_response.json()
    assert fetched["candidate_id"] == "candidate-test"

    trend_response = client.get("/api/feature2/candidate/candidate-test/trend")
    assert trend_response.status_code == 200

    forecast_response = client.get("/api/feature2/candidate/candidate-test/forecast")
    assert forecast_response.status_code == 200
