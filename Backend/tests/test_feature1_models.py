"""
Unit tests for Feature1Analysis database model schema.

Tests backward compatibility and default value handling for new fields:
- ai_recommendations_json (default: "[]")
- raw_resume_text (default: "")

Requirements: 1.5, 3.1, 3.2, 3.5
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from sqlmodel import Session, SQLModel, create_engine, select

from app.models import Feature1Analysis


@pytest.fixture
def test_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_session(test_engine):
    """Create a test database session."""
    with Session(test_engine) as session:
        yield session


def test_feature1_analysis_default_values(test_session):
    """Test that new fields have correct default values for backward compatibility."""
    # Create a minimal Feature1Analysis record without specifying new fields
    analysis = Feature1Analysis(
        candidate_id="test_candidate_001",
        job_category="software_engineer",
        resume_filename="test_resume.pdf",
        resume_path="/uploads/test_resume.pdf",
        version_number=1,
        overall_score=85.5,
        visual_score=90.0,
        ats_score=80.0,
        semantic_score=85.0,
        benchmark_score=88.0,
        eye_tracking_summary="Good visual hierarchy",
        ats_summary="ATS friendly",
        semantic_summary="Strong match",
        benchmark_summary="Above average",
        hotzones_json="[]",
        metrics_json="{}",
        recommendations_json="[]",
    )
    
    test_session.add(analysis)
    test_session.commit()
    test_session.refresh(analysis)
    
    # Verify new fields have correct defaults
    assert analysis.ai_recommendations_json == "[]"
    assert analysis.raw_resume_text == ""
    assert analysis.id is not None


def test_feature1_analysis_with_ai_recommendations(test_session):
    """Test storing and retrieving AI recommendations."""
    ai_recs = ["Improve technical skills section", "Add quantifiable achievements"]
    
    analysis = Feature1Analysis(
        candidate_id="test_candidate_002",
        job_category="data_scientist",
        resume_filename="resume2.pdf",
        resume_path="/uploads/resume2.pdf",
        version_number=1,
        overall_score=75.0,
        visual_score=80.0,
        ats_score=70.0,
        semantic_score=75.0,
        benchmark_score=72.0,
        eye_tracking_summary="Needs improvement",
        ats_summary="Some issues",
        semantic_summary="Moderate match",
        benchmark_summary="Below average",
        hotzones_json="[]",
        metrics_json="{}",
        recommendations_json="[]",
        ai_recommendations_json=json.dumps(ai_recs),
    )
    
    test_session.add(analysis)
    test_session.commit()
    test_session.refresh(analysis)
    
    # Verify AI recommendations are stored and retrieved correctly
    stored_recs = json.loads(analysis.ai_recommendations_json)
    assert stored_recs == ai_recs
    assert len(stored_recs) == 2


def test_feature1_analysis_with_raw_resume_text(test_session):
    """Test storing and retrieving raw resume text."""
    raw_text = "John Doe\nSoftware Engineer\nExperience: 5 years\nSkills: Python, SQL"
    
    analysis = Feature1Analysis(
        candidate_id="test_candidate_003",
        job_category="backend_engineer",
        resume_filename="resume3.pdf",
        resume_path="/uploads/resume3.pdf",
        version_number=1,
        overall_score=90.0,
        visual_score=92.0,
        ats_score=88.0,
        semantic_score=91.0,
        benchmark_score=89.0,
        eye_tracking_summary="Excellent",
        ats_summary="Perfect",
        semantic_summary="Strong match",
        benchmark_summary="Top tier",
        hotzones_json="[]",
        metrics_json="{}",
        recommendations_json="[]",
        raw_resume_text=raw_text,
    )
    
    test_session.add(analysis)
    test_session.commit()
    test_session.refresh(analysis)
    
    # Verify raw text is stored correctly
    assert analysis.raw_resume_text == raw_text


def test_feature1_analysis_text_truncation(test_session):
    """Test that raw resume text can handle truncation to 8000 characters."""
    # Create text longer than 8000 characters
    long_text = "A" * 10000
    truncated_text = long_text[:8000]
    
    analysis = Feature1Analysis(
        candidate_id="test_candidate_004",
        job_category="full_stack",
        resume_filename="resume4.pdf",
        resume_path="/uploads/resume4.pdf",
        version_number=1,
        overall_score=80.0,
        visual_score=82.0,
        ats_score=78.0,
        semantic_score=81.0,
        benchmark_score=79.0,
        eye_tracking_summary="Good",
        ats_summary="Good",
        semantic_summary="Good match",
        benchmark_summary="Average",
        hotzones_json="[]",
        metrics_json="{}",
        recommendations_json="[]",
        raw_resume_text=truncated_text,
    )
    
    test_session.add(analysis)
    test_session.commit()
    test_session.refresh(analysis)
    
    # Verify text is stored at 8000 characters
    assert len(analysis.raw_resume_text) == 8000
    assert analysis.raw_resume_text == truncated_text


def test_feature1_analysis_backward_compatibility_query(test_session):
    """Test that existing queries work with new fields."""
    # Create multiple analyses for the same candidate
    for i in range(3):
        analysis = Feature1Analysis(
            candidate_id="test_candidate_005",
            job_category="devops",
            resume_filename=f"resume_v{i+1}.pdf",
            resume_path=f"/uploads/resume_v{i+1}.pdf",
            version_number=i + 1,
            overall_score=80.0 + i,
            visual_score=80.0,
            ats_score=80.0,
            semantic_score=80.0,
            benchmark_score=80.0,
            eye_tracking_summary="Summary",
            ats_summary="Summary",
            semantic_summary="Summary",
            benchmark_summary="Summary",
            hotzones_json="[]",
            metrics_json="{}",
            recommendations_json="[]",
        )
        test_session.add(analysis)
    
    test_session.commit()
    
    # Query all analyses for the candidate (existing query pattern)
    query = (
        select(Feature1Analysis)
        .where(Feature1Analysis.candidate_id == "test_candidate_005")
        .order_by(Feature1Analysis.version_number.desc())
    )
    results = list(test_session.exec(query).all())
    
    # Verify query works and returns correct data
    assert len(results) == 3
    assert results[0].version_number == 3
    assert results[0].ai_recommendations_json == "[]"
    assert results[0].raw_resume_text == ""


def test_feature1_analysis_empty_ai_recommendations_parsing(test_session):
    """Test that empty AI recommendations can be safely parsed."""
    analysis = Feature1Analysis(
        candidate_id="test_candidate_006",
        job_category="frontend",
        resume_filename="resume6.pdf",
        resume_path="/uploads/resume6.pdf",
        version_number=1,
        overall_score=85.0,
        visual_score=85.0,
        ats_score=85.0,
        semantic_score=85.0,
        benchmark_score=85.0,
        eye_tracking_summary="Summary",
        ats_summary="Summary",
        semantic_summary="Summary",
        benchmark_summary="Summary",
        hotzones_json="[]",
        metrics_json="{}",
        recommendations_json="[]",
        ai_recommendations_json="[]",
    )
    
    test_session.add(analysis)
    test_session.commit()
    test_session.refresh(analysis)
    
    # Verify empty list can be parsed safely
    ai_recs = json.loads(analysis.ai_recommendations_json)
    assert ai_recs == []
    assert isinstance(ai_recs, list)


def test_feature1_analysis_both_new_fields_populated(test_session):
    """Test that both new fields can be populated simultaneously."""
    ai_recs = ["Recommendation 1", "Recommendation 2", "Recommendation 3"]
    raw_text = "Complete resume text content here"
    
    analysis = Feature1Analysis(
        candidate_id="test_candidate_007",
        job_category="ml_engineer",
        resume_filename="resume7.pdf",
        resume_path="/uploads/resume7.pdf",
        version_number=1,
        overall_score=92.0,
        visual_score=90.0,
        ats_score=94.0,
        semantic_score=92.0,
        benchmark_score=91.0,
        eye_tracking_summary="Excellent",
        ats_summary="Perfect",
        semantic_summary="Strong",
        benchmark_summary="Top",
        hotzones_json="[]",
        metrics_json="{}",
        recommendations_json="[]",
        ai_recommendations_json=json.dumps(ai_recs),
        raw_resume_text=raw_text,
    )
    
    test_session.add(analysis)
    test_session.commit()
    test_session.refresh(analysis)
    
    # Verify both fields are stored correctly
    assert json.loads(analysis.ai_recommendations_json) == ai_recs
    assert analysis.raw_resume_text == raw_text


def test_feature1_analysis_created_at_timestamp(test_session):
    """Test that created_at timestamp is automatically set."""
    analysis = Feature1Analysis(
        candidate_id="test_candidate_008",
        job_category="security",
        resume_filename="resume8.pdf",
        resume_path="/uploads/resume8.pdf",
        version_number=1,
        overall_score=88.0,
        visual_score=88.0,
        ats_score=88.0,
        semantic_score=88.0,
        benchmark_score=88.0,
        eye_tracking_summary="Summary",
        ats_summary="Summary",
        semantic_summary="Summary",
        benchmark_summary="Summary",
        hotzones_json="[]",
        metrics_json="{}",
        recommendations_json="[]",
    )
    
    test_session.add(analysis)
    test_session.commit()
    test_session.refresh(analysis)
    
    # Verify timestamp is set and is a datetime object
    assert analysis.created_at is not None
    assert isinstance(analysis.created_at, datetime)
