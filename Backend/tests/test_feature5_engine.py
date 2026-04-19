from app.analysis.feature5_engine import Feature5NarrativeEngine


def test_feature5_engine_full_session_builds():
    engine = Feature5NarrativeEngine()
    payload = engine.build_full_session(
        repo_subpath=".",
        target_role="Platform Engineer",
        tone="deep_tech",
        jd_text="fastapi python testing architecture",
        resume_text="Built fastapi services and tests",
        linkedin_text="Platform engineering with API design",
        github_repo="",
        selected_projects=["Backend", "Frontend"],
    )

    assert "epic_5_1" in payload["deep_analysis"]
    assert "epic_5_2" in payload["narrative"]
    assert "epic_5_3" in payload["talk_track"]
    assert "epic_5_4" in payload["gap_analysis"]
    assert "epic_5_5" in payload["export_sync"]
    assert "consistency_score" in payload["consistency_check"]
