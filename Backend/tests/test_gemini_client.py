"""
Unit tests for the Gemini API client.
Tests error handling, timeout behavior, and JSON parsing.
"""
import json
from unittest.mock import Mock, patch

import httpx
import pytest

from app.analysis import gemini_client


class TestGeminiClientAvailability:
    """Test API key availability checks."""
    
    def test_is_available_with_gemini_key(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            assert gemini_client.is_available() is True
    
    def test_is_available_with_google_key(self):
        with patch.dict("os.environ", {"GOOGLE_API_KEY": "test-key"}, clear=True):
            assert gemini_client.is_available() is True
    
    def test_is_available_without_key(self):
        with patch.dict("os.environ", {}, clear=True):
            assert gemini_client.is_available() is False
    
    def test_is_available_with_empty_key(self):
        with patch.dict("os.environ", {"GEMINI_API_KEY": "  "}):
            assert gemini_client.is_available() is False


class TestGeminiClientGenerate:
    """Test the generate() method with various scenarios."""
    
    def test_generate_success(self):
        """Test successful API call returns text."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "This is a test response"}
                        ]
                    }
                }
            ]
        }
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                
                result = gemini_client.generate("test prompt")
                assert result == "This is a test response"
    
    def test_generate_no_api_key(self):
        """Test that missing API key returns empty string."""
        with patch.dict("os.environ", {}, clear=True):
            result = gemini_client.generate("test prompt")
            assert result == ""
    
    def test_generate_timeout(self):
        """Test that timeout returns empty string and logs error."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")
                
                result = gemini_client.generate("test prompt")
                assert result == ""
    
    def test_generate_rate_limit_429(self):
        """Test that rate limit (429) returns empty string and logs error."""
        mock_response = Mock()
        mock_response.status_code = 429
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                
                result = gemini_client.generate("test prompt")
                assert result == ""
    
    def test_generate_server_error_500(self):
        """Test that server error (500) returns empty string."""
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                
                result = gemini_client.generate("test prompt")
                assert result == ""
    
    def test_generate_client_error_400(self):
        """Test that client error (400) returns empty string."""
        mock_response = Mock()
        mock_response.status_code = 400
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                
                result = gemini_client.generate("test prompt")
                assert result == ""
    
    def test_generate_malformed_json(self):
        """Test that malformed JSON response returns empty string."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                
                result = gemini_client.generate("test prompt")
                assert result == ""
    
    def test_generate_network_error(self):
        """Test that network error returns empty string."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.side_effect = httpx.NetworkError("Network error")
                
                result = gemini_client.generate("test prompt")
                assert result == ""
    
    def test_generate_unexpected_error(self):
        """Test that unexpected errors return empty string."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.side_effect = Exception("Unexpected error")
                
                result = gemini_client.generate("test prompt")
                assert result == ""
    
    def test_generate_empty_response(self):
        """Test that empty candidates list returns empty string."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"candidates": []}
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                
                result = gemini_client.generate("test prompt")
                assert result == ""
    
    def test_generate_missing_content(self):
        """Test that missing content field returns empty string."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [{"content": None}]
        }
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                
                result = gemini_client.generate("test prompt")
                assert result == ""
    
    def test_generate_multiple_parts(self):
        """Test that multiple text parts are joined correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {"text": "Part 1"},
                            {"text": "Part 2"},
                            {"text": "Part 3"}
                        ]
                    }
                }
            ]
        }
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.return_value = mock_response
                
                result = gemini_client.generate("test prompt")
                assert result == "Part 1\nPart 2\nPart 3"
    
    def test_generate_custom_temperature_and_tokens(self):
        """Test that custom temperature and max_tokens are passed correctly."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "Response"}]
                    }
                }
            ]
        }
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_post = mock_client.return_value.__enter__.return_value.post
                mock_post.return_value = mock_response
                
                gemini_client.generate("test prompt", temperature=0.3, max_tokens=400)
                
                # Verify the request body contains correct config
                call_args = mock_post.call_args
                request_body = call_args.kwargs["json"]
                assert request_body["generationConfig"]["temperature"] == 0.3
                assert request_body["generationConfig"]["maxOutputTokens"] == 400


class TestGeminiClientGenerateJson:
    """Test the generate_json() method."""
    
    def test_generate_json_wraps_prompt(self):
        """Test that generate_json wraps the prompt with JSON instructions."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": '{"key": "value"}'}]
                    }
                }
            ]
        }
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_post = mock_client.return_value.__enter__.return_value.post
                mock_post.return_value = mock_response
                
                result = gemini_client.generate_json("test prompt")
                
                # Verify the prompt was wrapped
                call_args = mock_post.call_args
                request_body = call_args.kwargs["json"]
                prompt_text = request_body["contents"][0]["parts"][0]["text"]
                assert "test prompt" in prompt_text
                assert "valid JSON only" in prompt_text
                assert result == '{"key": "value"}'
    
    def test_generate_json_uses_correct_defaults(self):
        """Test that generate_json uses temperature=0.2 and max_tokens=2048 by default."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": "{}"}]
                    }
                }
            ]
        }
        
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_post = mock_client.return_value.__enter__.return_value.post
                mock_post.return_value = mock_response
                
                gemini_client.generate_json("test prompt")
                
                # Verify the request body contains correct config
                call_args = mock_post.call_args
                request_body = call_args.kwargs["json"]
                assert request_body["generationConfig"]["temperature"] == 0.2
                assert request_body["generationConfig"]["maxOutputTokens"] == 2048
    
    def test_generate_json_fallback_on_error(self):
        """Test that generate_json returns empty string on error."""
        with patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"}):
            with patch("httpx.Client") as mock_client:
                mock_client.return_value.__enter__.return_value.post.side_effect = httpx.TimeoutException("Timeout")
                
                result = gemini_client.generate_json("test prompt")
                assert result == ""


class TestGeminiClientTimeout:
    """Test timeout configuration."""
    
    def test_timeout_is_20_seconds(self):
        """Test that the timeout is set to 20 seconds as per requirements."""
        assert gemini_client._TIMEOUT == 20.0
