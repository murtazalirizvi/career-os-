from app.analysis.feature3_engine import FutureEngine, MarketIntelligenceEngine, RoiEngine, SkillGapEngine, SprintEngine


def test_feature3_market_snapshot_has_required_sections():
    engine = MarketIntelligenceEngine()
    payload = engine.build_market_snapshot(
        target_role="Backend Engineer",
        region="PK",
        remote_only=False,
        search_terms=["python", "sql"],
    )

    assert "jobs" in payload
    assert "tech_stack_clusters" in payload
    assert "demand_supply_ratio" in payload
    assert "salary_to_skill_map" in payload
    assert "remote_opportunity_filter" in payload
    assert len(payload["jobs"]) > 0


def test_feature3_gap_sprint_future_roi_pipeline():
    market_engine = MarketIntelligenceEngine()
    gap_engine = SkillGapEngine()
    sprint_engine = SprintEngine()
    future_engine = FutureEngine()
    roi_engine = RoiEngine()

    market = market_engine.build_market_snapshot(
        target_role="Fullstack Engineer",
        region="PK",
        remote_only=True,
        search_terms=["react", "python"],
    )

    gap = gap_engine.build_gap_analysis(
        current_skills=["react", "javascript", "python"],
        years_experience=2.0,
        market_snapshot=market,
        github_username="",
        historical_rows=[],
    )

    sprint = sprint_engine.build_sprint(primary_skill="kubernetes", target_role="Fullstack Engineer")
    quiz_result = sprint_engine.evaluate_quiz(
        quiz=sprint["quick_quiz"],
        answers=[
            "Trade-off is latency vs consistency with reliability checks and tests.",
            "Failure mode is stale state; mitigate via constraints and retries.",
            "Result: reduced incident rate by 20 percent with measurable impact.",
        ],
    )

    future = future_engine.build_future_insights(
        current_skills=["python", "llm", "agents", "testing", "ci"],
        market_snapshot=market,
    )
    roi = roi_engine.build_roi(
        current_salary_usd=12000,
        target_path="fullstack",
        gap_snapshot=gap,
        market_snapshot=market,
    )

    assert gap["match_score"] >= 0
    assert "roadmap_to_90" in gap
    assert len(sprint["curated_day_plan"]) == 7
    assert quiz_result["score"] >= 0
    assert "agentic_ai_score" in future
    assert "callback_probability" in roi
