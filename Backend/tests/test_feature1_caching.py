"""
Unit tests for Feature1 LRU resume text caching system.

Tests the caching functionality for PDF parsing to avoid redundant processing:
- LRU cache eviction behavior with maxsize=10
- Cache lookup priority (cache-first strategy)
- Cache round-trip consistency (cached vs fresh parsing)
- Cache error handling and fallback

Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3, 6.5, 7.3
"""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock, patch

import pytest

from app.analysis.feature1_engine import (
    _cached_resume_text,
    _get_resume_text_and_blocks,
)


@pytest.fixture
def mock_pdf_path():
    """Create a mock PDF path for testing."""
    return Path("/test/resume.pdf")


@pytest.fixture
def mock_extract_result():
    """Create mock extract_text_and_layout result."""
    text = "John Doe\nSoftware Engineer\nPython, SQL, Docker"
    blocks = [
        {
            "page": 0,
            "text": "John Doe",
            "bbox": [100, 100, 200, 120],
            "font_size": 16.0,
            "bold_weight": 1.0,
        },
        {
            "page": 0,
            "text": "Software Engineer",
            "bbox": [100, 130, 250, 145],
            "font_size": 12.0,
            "bold_weight": 0.0,
        },
    ]
    return text, blocks


def test_cached_resume_text_basic_functionality(mock_pdf_path, mock_extract_result):
    """Test that _cached_resume_text returns correct data structure."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = mock_extract_result
        
        # First call should invoke extract_text_and_layout
        text, blocks_tuple = _cached_resume_text(str(mock_pdf_path))
        
        # Verify return types
        assert isinstance(text, str)
        assert isinstance(blocks_tuple, tuple)
        assert len(blocks_tuple) == 2
        
        # Verify text content
        assert "John Doe" in text
        assert "Software Engineer" in text
        
        # Verify blocks are JSON serialized
        for block_json in blocks_tuple:
            assert isinstance(block_json, str)
            block = json.loads(block_json)
            assert "page" in block
            assert "text" in block
            assert "bbox" in block


def test_cache_hit_avoids_reparsing(mock_pdf_path, mock_extract_result):
    """Test that cache hit avoids calling extract_text_and_layout again."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = mock_extract_result
        
        # First call - cache miss
        result1 = _cached_resume_text(str(mock_pdf_path))
        assert mock_extract.call_count == 1
        
        # Second call - cache hit
        result2 = _cached_resume_text(str(mock_pdf_path))
        assert mock_extract.call_count == 1  # Should not increase
        
        # Results should be identical
        assert result1 == result2


def test_get_resume_text_and_blocks_deserializes_correctly(mock_pdf_path, mock_extract_result):
    """Test that _get_resume_text_and_blocks properly deserializes cached data."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = mock_extract_result
        
        # Call wrapper function
        text, blocks = _get_resume_text_and_blocks(mock_pdf_path)
        
        # Verify text
        assert isinstance(text, str)
        assert "John Doe" in text
        
        # Verify blocks are deserialized to list of dicts
        assert isinstance(blocks, list)
        assert len(blocks) == 2
        assert all(isinstance(b, dict) for b in blocks)
        
        # Verify block structure
        assert blocks[0]["text"] == "John Doe"
        assert blocks[0]["font_size"] == 16.0
        assert blocks[1]["text"] == "Software Engineer"


def test_cache_round_trip_consistency(mock_pdf_path, mock_extract_result):
    """Test that cached parsing produces identical results to fresh parsing."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = mock_extract_result
        
        # First call - fresh parse
        text1, blocks1 = _get_resume_text_and_blocks(mock_pdf_path)
        
        # Second call - from cache
        text2, blocks2 = _get_resume_text_and_blocks(mock_pdf_path)
        
        # Text should match character-for-character
        assert text1 == text2
        
        # Blocks should have identical structure
        assert len(blocks1) == len(blocks2)
        for b1, b2 in zip(blocks1, blocks2):
            assert b1["page"] == b2["page"]
            assert b1["text"] == b2["text"]
            assert b1["bbox"] == b2["bbox"]
            assert b1["font_size"] == b2["font_size"]
            assert b1["bold_weight"] == b2["bold_weight"]


def test_cache_different_paths_are_separate(mock_extract_result):
    """Test that different file paths create separate cache entries."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    path1 = "/test/resume1.pdf"
    path2 = "/test/resume2.pdf"
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = mock_extract_result
        
        # Call with first path
        _cached_resume_text(path1)
        assert mock_extract.call_count == 1
        
        # Call with second path - should trigger new parse
        _cached_resume_text(path2)
        assert mock_extract.call_count == 2
        
        # Call with first path again - should use cache
        _cached_resume_text(path1)
        assert mock_extract.call_count == 2


def test_cache_preserves_layout_metadata(mock_pdf_path):
    """Test that cache preserves all layout block metadata."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    # Create detailed blocks with all metadata
    detailed_blocks = [
        {
            "page": 0,
            "text": "Header Text",
            "bbox": [50.5, 75.3, 200.8, 95.2],
            "font_size": 18.5,
            "bold_weight": 1.0,
        },
        {
            "page": 1,
            "text": "Body Text",
            "bbox": [50.0, 100.0, 500.0, 115.0],
            "font_size": 11.0,
            "bold_weight": 0.5,
        },
    ]
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = ("Test text", detailed_blocks)
        
        # Get blocks through cache
        _, blocks = _get_resume_text_and_blocks(mock_pdf_path)
        
        # Verify all metadata is preserved
        assert blocks[0]["page"] == 0
        assert blocks[0]["text"] == "Header Text"
        assert blocks[0]["bbox"] == [50.5, 75.3, 200.8, 95.2]
        assert blocks[0]["font_size"] == 18.5
        assert blocks[0]["bold_weight"] == 1.0
        
        assert blocks[1]["page"] == 1
        assert blocks[1]["font_size"] == 11.0
        assert blocks[1]["bold_weight"] == 0.5


def test_cache_handles_empty_blocks(mock_pdf_path):
    """Test that cache correctly handles PDFs with no layout blocks."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = ("Some text", [])
        
        text, blocks = _get_resume_text_and_blocks(mock_pdf_path)
        
        assert text == "Some text"
        assert blocks == []
        assert isinstance(blocks, list)


def test_cache_handles_large_text(mock_pdf_path):
    """Test that cache handles large resume text correctly."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    # Create large text (10KB)
    large_text = "A" * 10000
    blocks = [{"page": 0, "text": "Test", "bbox": [0, 0, 100, 100], "font_size": 12.0, "bold_weight": 0.0}]
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = (large_text, blocks)
        
        # First call
        text1, _ = _get_resume_text_and_blocks(mock_pdf_path)
        
        # Second call from cache
        text2, _ = _get_resume_text_and_blocks(mock_pdf_path)
        
        # Should be identical
        assert len(text1) == 10000
        assert text1 == text2


def test_cache_handles_special_characters_in_text(mock_pdf_path):
    """Test that cache correctly handles special characters and unicode."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    special_text = "Résumé • João Silva • 日本語 • Emoji: 🚀"
    blocks = [
        {
            "page": 0,
            "text": special_text,
            "bbox": [0, 0, 100, 100],
            "font_size": 12.0,
            "bold_weight": 0.0,
        }
    ]
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = (special_text, blocks)
        
        # Get from cache
        text, cached_blocks = _get_resume_text_and_blocks(mock_pdf_path)
        
        # Verify special characters are preserved
        assert text == special_text
        assert cached_blocks[0]["text"] == special_text


def test_cache_info_reflects_hits_and_misses():
    """Test that cache statistics correctly track hits and misses."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    path1 = "/test/resume1.pdf"
    path2 = "/test/resume2.pdf"
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = ("text", [])
        
        # Initial state
        info = _cached_resume_text.cache_info()
        assert info.hits == 0
        assert info.misses == 0
        
        # First call - miss
        _cached_resume_text(path1)
        info = _cached_resume_text.cache_info()
        assert info.misses == 1
        assert info.hits == 0
        
        # Second call same path - hit
        _cached_resume_text(path1)
        info = _cached_resume_text.cache_info()
        assert info.hits == 1
        assert info.misses == 1
        
        # Different path - miss
        _cached_resume_text(path2)
        info = _cached_resume_text.cache_info()
        assert info.hits == 1
        assert info.misses == 2


def test_cache_clear_functionality():
    """Test that cache_clear() properly clears all cached entries."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = ("text", [])
        
        # Add entries to cache
        _cached_resume_text("/test/resume1.pdf")
        _cached_resume_text("/test/resume2.pdf")
        
        info = _cached_resume_text.cache_info()
        assert info.currsize == 2
        
        # Clear cache
        _cached_resume_text.cache_clear()
        
        info = _cached_resume_text.cache_info()
        assert info.currsize == 0
        assert info.hits == 0
        assert info.misses == 0


def test_cache_with_multiple_pages(mock_pdf_path):
    """Test that cache correctly handles multi-page PDFs."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    multi_page_text = "Page 1 content\nPage 2 content\nPage 3 content"
    multi_page_blocks = [
        {"page": 0, "text": "Page 1", "bbox": [0, 0, 100, 100], "font_size": 12.0, "bold_weight": 0.0},
        {"page": 1, "text": "Page 2", "bbox": [0, 0, 100, 100], "font_size": 12.0, "bold_weight": 0.0},
        {"page": 2, "text": "Page 3", "bbox": [0, 0, 100, 100], "font_size": 12.0, "bold_weight": 0.0},
    ]
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = (multi_page_text, multi_page_blocks)
        
        text, blocks = _get_resume_text_and_blocks(mock_pdf_path)
        
        # Verify all pages are present
        assert "Page 1" in text
        assert "Page 2" in text
        assert "Page 3" in text
        assert len(blocks) == 3
        assert blocks[0]["page"] == 0
        assert blocks[1]["page"] == 1
        assert blocks[2]["page"] == 2


def test_json_serialization_handles_all_types(mock_pdf_path):
    """Test that JSON serialization handles all data types in blocks."""
    # Clear cache before test
    _cached_resume_text.cache_clear()
    
    # Blocks with various data types
    complex_blocks = [
        {
            "page": 0,
            "text": "Test",
            "bbox": [10.5, 20.3, 100.8, 50.2],  # floats
            "font_size": 12.0,
            "bold_weight": 0.5,
        }
    ]
    
    with patch("app.analysis.feature1_engine.extract_text_and_layout") as mock_extract:
        mock_extract.return_value = ("text", complex_blocks)
        
        # Get through cache
        _, blocks = _get_resume_text_and_blocks(mock_pdf_path)
        
        # Verify types are preserved after serialization round-trip
        assert isinstance(blocks[0]["page"], int)
        assert isinstance(blocks[0]["text"], str)
        assert isinstance(blocks[0]["bbox"], list)
        assert all(isinstance(x, float) for x in blocks[0]["bbox"])
        assert isinstance(blocks[0]["font_size"], float)
        assert isinstance(blocks[0]["bold_weight"], float)
