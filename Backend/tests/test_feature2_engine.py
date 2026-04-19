from app.analysis.feature2_engine import Feature2Engine


def build_engine() -> Feature2Engine:
    return Feature2Engine(
        interview_notes="I was asked about SQL indexes and caching, I froze at first but recovered.",
        transcript_text="Interviewer: How would you optimize query latency? Candidate: I would definitely add cache but I am not sure about invalidation.",
        transcript_vtt="",
        technical_expectations=["sql", "cache", "api"],
        culture_vibe="neutral",
        interviewer_friendliness=6,
        interview_round="tech",
        lifecycle_stage="tech",
        hardest_question_hint="",
        advanced_round_reached=False,
        rejection_reason_hint="technical depth",
        interview_outcome="rejected",
    )


def test_feature2_run_has_all_sections():
    result = build_engine().run()

    assert "ingestion" in result
    assert "technical" in result
    assert "behavioral" in result
    assert "strategic_actions" in result
    assert "score" in result

    assert result["technical"]["semantic_correctness"] >= 0
    assert result["behavioral"]["filler_word_count"] >= 0
    assert "clarification_email" in result["strategic_actions"]


def test_feature2_quick_debrief_extracts_actions():
    result = build_engine().quick_debrief("I froze and then rambled, I did not know Redis invalidation")

    assert result["extracted_hardest_question"]
    assert isinstance(result["top_failure_themes"], list)
    assert isinstance(result["immediate_next_actions"], list)
    assert len(result["immediate_next_actions"]) > 0
