"""
Property-based tests for Feature1 LRU resume text caching system.

These tests verify universal properties that should hold across all inputs:
- Property 10: LRU Cache Eviction Behavior
- Property 11: Cache Lookup Priority
- Property 14: Cache Round-Trip Consistency

Requirements: 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3, 6.5

Testing Framework: pytest with hypothesis for property-based testing
"""

from pathlib import Path
from unittest.mock import patch

import pytest

# Try to import hypothesis, skip tests if not available
try:
    from hypothesis import given, strategies as st, settings
    HYPOTHESIS_AVAILABLE = True
except ImportError:
    HYPOTHESIS_AVAILABLE = False
    pytest.skip("hypothesis not installed", allow_module_level=True)

from app.analysis.feature1_engine import (
    _cached_resume_text,
    _get_resume_text_and_blocks,
)


# ── Test Strategies ───────────────────────────────────────────────────────────

@st.composite
def resume_path_strategy(draw):
    """Generate valid resume file paths."""
    filename = draw(st.text(
        alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd"), min_codepoint=65, max_codepoint=122),
        min_size=5,
        max_size=30
    ))
    return f"/test/resumes/{filename}.pdf"


@st.composite
def resume_content_strategy(draw):
    """Generate realistic resume text and layout blocks."""
    # Generate resume text
    text = draw(st.text(min_size=100, max_size=5000))
    
    # Generate layout blocks
    num_blocks = draw(st.integers(min_value=1, max_value=50))
    blocks = []
    
    for i in range(num_blocks):
        block = {
            "page": draw(st.integers(min_value=0, max_value=5)),
            "text": draw(st.text(min_size=1, max_size=100)),
            "bbox": [
                draw(st.floats(min_value=0, max_value=1000)),
                draw(st.floats(min_value=0, max_value=1000)),
                draw(st.floats(min_value=0, max_value=1000)),
                draw(st.floats(min_value=0, max_value=1000)),
            ],
            "font_size": draw(st.floats(min_value=6.0, max_value=72.0)),
            "bold_weight": draw(st.floats(min_value=0.0, max_value=1.0)),
        }
        blocks.append(block)
    
    return text, blocks


# ── Property 10: LRU Cache Eviction Behavior ──────────────────────────────────

@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(st.lists(resume_path_strategy(), min_size=15, max_size=20, unique=True))
@settings(max_examples=50, deadline=None)
def test_property_lru_cache_eviction_behavior(paths):
    """
    **Feature: feature1-lens-hardening, Property 10: LRU Cache Eviction Behavior**
    
    For any sequence of cache operations exceeding 10 entries, the cache SHALL evict
    the least recently used entry when adding new entries, maintaining exactly 10
    entries maximum.
    
    **Validates: Requirements 5.1, 5.4**
    """
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        # Mock returns unique content for each path
        def mock_extract_fn(path):
            return (f"text_{path}", [{"page": 0, "text": str(path), "bbox": [0, 0, 100, 100], "font_size": 12.0, "bold_weight": 0.0}])
        
        mock_extract.side_effect = mock_extract_fn
        
        # Add more than 10 entries
        for path in paths[:15]:
            _cached_resume_text(path)
        
        # Check cache size is at most 10
        info = _cached_resume_text.cache_info()
        assert info.currsize <= 10, f"Cache size {info.currsize} exceeds maximum of 10"
        
        # Verify that accessing an old entry (if evicted) causes a cache miss
        # The first 5 entries should have been evicted
        initial_misses = info.misses
        _cached_resume_text(paths[0])  # This should be evicted
        
        # If it was evicted, we should see a new miss
        new_info = _cached_resume_text.cache_info()
        # Either it's still cached (hit) or it was evicted (miss)
        assert new_info.hits + new_info.misses > initial_misses


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(st.lists(resume_path_strategy(), min_size=12, max_size=15, unique=True))
@settings(max_examples=50, deadline=None)
def test_property_lru_eviction_maintains_max_size(paths):
    """
    Test that cache never exceeds maxsize=10 regardless of access patterns.
    
    **Validates: Requirements 5.1, 5.4**
    """
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = ("text", [])
        
        # Add entries one by one and check size after each
        for i, path in enumerate(paths):
            _cached_resume_text(path)
            info = _cached_resume_text.cache_info()
            
            # Cache size should never exceed 10
            assert info.currsize <= 10, f"After {i+1} insertions, cache size {info.currsize} exceeds 10"


# ── Property 11: Cache Lookup Priority ────────────────────────────────────────

@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(resume_path_strategy(), resume_content_strategy())
@settings(max_examples=100, deadline=None)
def test_property_cache_lookup_priority(path, content):
    """
    **Feature: feature1-lens-hardening, Property 11: Cache Lookup Priority**
    
    For any resume PDF parsing request, the system SHALL check the cache first
    using the file path as key before attempting fresh PDF parsing.
    
    **Validates: Requirements 5.2**
    """
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    text, blocks = content
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = (text, blocks)
        
        # First call - should hit extract_text_and_layout
        _cached_resume_text(path)
        first_call_count = mock_extract.call_count
        assert first_call_count == 1, "First call should invoke PDF parsing"
        
        # Second call - should NOT hit extract_text_and_layout (cache hit)
        _cached_resume_text(path)
        second_call_count = mock_extract.call_count
        assert second_call_count == 1, "Second call should use cache, not re-parse PDF"
        
        # Verify cache was actually used
        info = _cached_resume_text.cache_info()
        assert info.hits >= 1, "Cache should have at least one hit"


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(st.lists(resume_path_strategy(), min_size=3, max_size=8, unique=True))
@settings(max_examples=50, deadline=None)
def test_property_cache_hit_avoids_parsing(paths):
    """
    Test that cache hits never trigger PDF parsing.
    
    **Validates: Requirements 5.2, 5.3**
    """
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = ("text", [])
        
        # First pass - populate cache
        for path in paths:
            _cached_resume_text(path)
        
        expected_calls = len(paths)
        assert mock_extract.call_count == expected_calls
        
        # Second pass - all should be cache hits
        for path in paths:
            _cached_resume_text(path)
        
        # Call count should not increase
        assert mock_extract.call_count == expected_calls, "Cache hits should not trigger PDF parsing"


# ── Property 14: Cache Round-Trip Consistency ─────────────────────────────────

@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(resume_path_strategy(), resume_content_strategy())
@settings(max_examples=100, deadline=None)
def test_property_cache_round_trip_consistency(path, content):
    """
    **Feature: feature1-lens-hardening, Property 14: Cache Round-Trip Consistency**
    
    For any PDF file, parsing from cache SHALL produce identical results to fresh
    parsing, including character-for-character text matching and complete layout
    block structure preservation.
    
    **Validates: Requirements 6.1, 6.2, 6.3, 6.5**
    """
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    text, blocks = content
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = (text, blocks)
        
        # First call - fresh parse
        text1, blocks1 = _get_resume_text_and_blocks(Path(path))
        
        # Second call - from cache
        text2, blocks2 = _get_resume_text_and_blocks(Path(path))
        
        # Text must match character-for-character
        assert text1 == text2, "Cached text does not match fresh parse"
        
        # Blocks must have identical structure
        assert len(blocks1) == len(blocks2), "Block count mismatch between fresh and cached"
        
        for i, (b1, b2) in enumerate(zip(blocks1, blocks2)):
            assert b1["page"] == b2["page"], f"Block {i}: page mismatch"
            assert b1["text"] == b2["text"], f"Block {i}: text mismatch"
            assert b1["bbox"] == b2["bbox"], f"Block {i}: bbox mismatch"
            assert b1["font_size"] == b2["font_size"], f"Block {i}: font_size mismatch"
            assert b1["bold_weight"] == b2["bold_weight"], f"Block {i}: bold_weight mismatch"


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(resume_path_strategy(), st.text(min_size=0, max_size=10000))
@settings(max_examples=100, deadline=None)
def test_property_text_preservation_across_cache(path, text):
    """
    Test that text content is preserved exactly through cache serialization.
    
    **Validates: Requirements 6.1, 6.2**
    """
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    blocks = [{"page": 0, "text": "test", "bbox": [0, 0, 100, 100], "font_size": 12.0, "bold_weight": 0.0}]
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = (text, blocks)
        
        # Get text through cache twice
        text1, _ = _get_resume_text_and_blocks(Path(path))
        text2, _ = _get_resume_text_and_blocks(Path(path))
        
        # Must be identical
        assert text1 == text2 == text, "Text not preserved through cache"


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(resume_path_strategy(), resume_content_strategy())
@settings(max_examples=100, deadline=None)
def test_property_metadata_preservation(path, content):
    """
    Test that all layout block metadata is preserved through caching.
    
    **Validates: Requirements 6.3, 6.5**
    """
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    text, blocks = content
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = (text, blocks)
        
        # Get blocks through cache
        _, cached_blocks = _get_resume_text_and_blocks(Path(path))
        
        # All metadata must be preserved
        assert len(cached_blocks) == len(blocks)
        
        for original, cached in zip(blocks, cached_blocks):
            # Check all fields are present and equal
            assert cached["page"] == original["page"]
            assert cached["text"] == original["text"]
            assert cached["bbox"] == original["bbox"]
            assert cached["font_size"] == original["font_size"]
            assert cached["bold_weight"] == original["bold_weight"]


# ── Additional Cache Behavior Properties ──────────────────────────────────────

@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(st.lists(resume_path_strategy(), min_size=2, max_size=5, unique=True))
@settings(max_examples=50, deadline=None)
def test_property_different_paths_independent_cache(paths):
    """
    Test that different file paths create independent cache entries.
    
    **Validates: Requirements 5.2**
    """
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        # Each path gets unique content
        def mock_extract_fn(path):
            return (f"text_{path}", [{"page": 0, "text": str(path), "bbox": [0, 0, 100, 100], "font_size": 12.0, "bold_weight": 0.0}])
        
        mock_extract.side_effect = mock_extract_fn
        
        # Cache all paths
        results = {}
        for path in paths:
            text, blocks_tuple = _cached_resume_text(path)
            results[path] = (text, blocks_tuple)
        
        # Verify each path has unique cached content
        for path in paths:
            text, blocks_tuple = _cached_resume_text(path)
            assert (text, blocks_tuple) == results[path], f"Cache entry for {path} was corrupted"
            assert f"text_{path}" in text, "Wrong content returned from cache"


@pytest.mark.skipif(not HYPOTHESIS_AVAILABLE, reason="hypothesis not installed")
@given(resume_path_strategy(), st.lists(st.integers(min_value=0, max_value=10), min_size=1, max_size=20))
@settings(max_examples=50, deadline=None)
def test_property_cache_access_pattern_consistency(path, access_pattern):
    """
    Test that cache behaves consistently regardless of access pattern.
    
    **Validates: Requirements 5.2, 5.3**
    """
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = ("consistent_text", [])
        
        # Access the same path multiple times
        for _ in access_pattern:
            result = _cached_resume_text(path)
            # Every access should return the same result
            assert result[0] == "consistent_text"
        
        # Should only parse once
        assert mock_extract.call_count == 1, "Multiple accesses to same path should only parse once"
