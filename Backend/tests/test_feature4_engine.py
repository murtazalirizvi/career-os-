from app.analysis.feature4_engine import Feature4PersonaPlayEngine


def test_feature4_engine_core_flow():
    engine = Feature4PersonaPlayEngine()
    persona = engine.select_persona("blind")

    questions = engine.opening_questions(persona, "Backend Engineer")
    assert len(questions) >= 5

    rt = engine.analyze_realtime(
        utterance="I used cache with trade-off between latency and consistency, but maybe I needed better invalidation.",
        response_latency_ms=1800,
        audio_pitch_variance=0.62,
        silent_seconds=1.2,
        gaze_focus_ratio=0.74,
    )
    deep = engine.deep_logic_probe(persona, "Trade-off was latency versus consistency and cost.")
    hint = engine.whisper_hint(rt, deep)
    nq = engine.next_question(persona, 2, deep)

    assert "filler_tracker" in rt
    assert "tradeoff_trigger" in deep
    assert isinstance(hint, str) and len(hint) > 0
    assert "question" in nq


def test_feature4_finalize_and_synthesis():
    engine = Feature4PersonaPlayEngine()
    persona = engine.select_persona("stone_faced")

    turns = [
        {
            "question": {"type": "tradeoff_trigger", "question": "What trade-off?"},
            "utterance": "I chose lower latency over perfect consistency and documented rollback.",
            "realtime": engine.analyze_realtime("I chose lower latency over perfect consistency and documented rollback.", 1200, 0.58, 0.5, 0.8),
            "deep_logic": engine.deep_logic_probe(persona, "trade-off latency consistency rollback"),
        }
    ]

    final = engine.finalize_feedback(persona, turns, previous_summaries=[])
    assert "scorecard" in final
    assert "badges" in final

    synthesis = engine.synthesize_media(
        session_id=1,
        transcript_breakdown=final["transcript_breakdown"],
        voice_style="calm",
        avatar_style="mentor",
        language="hinglish",
        environment_theme="zoom",
    )
    assert "low_latency_audio" in synthesis
    assert synthesis["multilingual_pack"]["primary"] in {"hinglish", "english"}
