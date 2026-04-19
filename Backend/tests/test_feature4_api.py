from fastapi.testclient import TestClient

from app.db import create_db_and_tables
from app.main import app

create_db_and_tables()
client = TestClient(app)


def test_feature4_api_session_flow():
    create = client.post(
        "/api/feature4/sessions",
        json={
            "candidate_id": "candidate-f4",
            "role_name": "Backend Engineer",
            "persona_mode": "blind",
            "language": "english",
            "include_video": True,
            "environment_theme": "zoom",
        },
    )
    assert create.status_code == 200
    session_data = create.json()
    sid = session_data["session_id"]

    turn = client.post(
        f"/api/feature4/sessions/{sid}/turn",
        json={
            "utterance": "I reduced latency with caching while handling consistency with write-through and rollback.",
            "response_latency_ms": 1800,
            "audio_pitch_variance": 0.57,
            "silent_seconds": 1.4,
            "gaze_focus_ratio": 0.73,
        },
    )
    assert turn.status_code == 200
    turn_payload = turn.json()
    assert "realtime_signals" in turn_payload

    finalize = client.post(f"/api/feature4/sessions/{sid}/finalize")
    assert finalize.status_code == 200
    final_payload = finalize.json()
    assert "scorecard" in final_payload

    synthesis = client.post(
        f"/api/feature4/sessions/{sid}/synthesis",
        json={
            "voice_style": "calm",
            "avatar_style": "mentor",
            "language": "hinglish",
            "environment_theme": "office",
        },
    )
    assert synthesis.status_code == 200
    assert "low_latency_audio" in synthesis.json()

    share = client.post(f"/api/feature4/sessions/{sid}/share")
    assert share.status_code == 200
    token = share.json()["share_token"]

    shared_view = client.get(f"/api/feature4/share/{token}")
    assert shared_view.status_code == 200
    assert shared_view.json()["session_id"] == sid


def test_feature4_heatmap_compare():
    s1 = client.post(
        "/api/feature4/sessions",
        json={
            "candidate_id": "candidate-f4-compare",
            "role_name": "Backend Engineer",
            "persona_mode": "stone_faced",
        },
    ).json()["session_id"]

    s2 = client.post(
        "/api/feature4/sessions",
        json={
            "candidate_id": "candidate-f4-compare",
            "role_name": "Backend Engineer",
            "persona_mode": "deep_diver",
        },
    ).json()["session_id"]

    for sid in (s1, s2):
        client.post(
            f"/api/feature4/sessions/{sid}/turn",
            json={
                "utterance": "Trade-off was latency versus consistency with clear rollback metrics.",
                "response_latency_ms": 1700,
                "audio_pitch_variance": 0.55,
                "silent_seconds": 1.2,
                "gaze_focus_ratio": 0.76,
            },
        )
        client.post(f"/api/feature4/sessions/{sid}/finalize")

    cmp_resp = client.get(
        f"/api/feature4/candidate/candidate-f4-compare/heatmap-compare?left_session={s1}&right_session={s2}"
    )
    assert cmp_resp.status_code == 200
    payload = cmp_resp.json()
    assert payload["left_session"] == s1
    assert payload["right_session"] == s2
    assert "delta" in payload

    history = client.get("/api/feature4/candidate/candidate-f4-compare/sessions")
    assert history.status_code == 200
    hist_payload = history.json()
    assert len(hist_payload["sessions"]) >= 2
