"""
Unit tests for API retry logic functionality in BioGen.py
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock
import requests
import openai
import random
import sys
import os

# Add the project root to the path so we can import from BioGen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from BioGen import retry_api_call
except ImportError:
    # Mock the decorator if import fails during test discovery
    def retry_api_call(max_retries=3, backoff_factor=1.0):
        def decorator(func):
            return func
        return decorator

@pytest.mark.unit
class TestRetryApiCall:
    """Test cases for the retry_api_call decorator."""
    
    def test_retry_api_call_success_first_attempt(self):
        """Test that successful function calls work without retry."""
        @retry_api_call(max_retries=3, backoff_factor=0.1)
        def mock_api_function():
            return "success"
        
        result = mock_api_function()
        assert result == "success"
    
    def test_retry_api_call_success_after_failures(self):
        """Test that function succeeds after some failures."""
        call_count = 0
        
        @retry_api_call(max_retries=3, backoff_factor=0.1)
        def mock_api_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise requests.RequestException("Temporary failure")
            return "success"
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with patch('streamlit.warning'):  # Mock streamlit warning
                result = mock_api_function()
        
        assert result == "success"
        assert call_count == 3
    
    def test_retry_api_call_max_retries_exceeded_requests_exception(self):
        """Test that RequestException is raised after max retries."""
        call_count = 0
        
        @retry_api_call(max_retries=2, backoff_factor=0.1)
        def mock_api_function():
            nonlocal call_count
            call_count += 1
            raise requests.RequestException("Persistent failure")
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with patch('streamlit.warning'):  # Mock streamlit warning
                with pytest.raises(requests.RequestException):
                    mock_api_function()
        
        assert call_count == 3  # Initial attempt + 2 retries
    
    def test_retry_api_call_max_retries_exceeded_openai_error(self):
        """Test that OpenAIError is raised after max retries."""
        call_count = 0
        
        @retry_api_call(max_retries=2, backoff_factor=0.1)
        def mock_api_function():
            nonlocal call_count
            call_count += 1
            raise openai.OpenAIError("API quota exceeded")
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with patch('streamlit.warning'):  # Mock streamlit warning
                with pytest.raises(openai.OpenAIError):
                    mock_api_function()
        
        assert call_count == 3  # Initial attempt + 2 retries
    
    def test_retry_api_call_connection_error(self):
        """Test that ConnectionError is handled properly."""
        @retry_api_call(max_retries=1, backoff_factor=0.1)
        def mock_api_function():
            raise ConnectionError("Network unreachable")
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with patch('streamlit.warning'):  # Mock streamlit warning
                with pytest.raises(ConnectionError):
                    mock_api_function()
    
    def test_retry_api_call_non_retryable_exception(self):
        """Test that non-retryable exceptions are not retried."""
        call_count = 0
        
        @retry_api_call(max_retries=3, backoff_factor=0.1)
        def mock_api_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Invalid input")  # Not a retryable exception
        
        with pytest.raises(ValueError):
            mock_api_function()
        
        assert call_count == 1  # Should not retry
    
    def test_retry_api_call_exponential_backoff_timing(self):
        """Test that exponential backoff timing works correctly."""
        call_times = []
        
        @retry_api_call(max_retries=2, backoff_factor=1.0)
        def mock_api_function():
            call_times.append(time.time())
            raise requests.RequestException("Temporary failure")
        
        # Mock random.uniform to return predictable values
        with patch('random.uniform', return_value=0.0):
            with patch('streamlit.warning'):  # Mock streamlit warning
                # Mock time.sleep and capture the delay values
                sleep_delays = []
                def mock_sleep(delay):
                    sleep_delays.append(delay)
                
                with patch('time.sleep', side_effect=mock_sleep):
                    with pytest.raises(requests.RequestException):
                        mock_api_function()
        
        # Check that delays follow exponential backoff: 1.0, 2.0
        assert len(sleep_delays) == 2
        assert sleep_delays[0] == 1.0  # backoff_factor * (2^0) + 0
        assert sleep_delays[1] == 2.0  # backoff_factor * (2^1) + 0
    
    def test_retry_api_call_with_function_arguments(self):
        """Test that function arguments are passed correctly through retries."""
        call_args = []
        
        @retry_api_call(max_retries=2, backoff_factor=0.1)
        def mock_api_function(arg1, arg2, kwarg1=None):
            call_args.append((arg1, arg2, kwarg1))
            if len(call_args) < 2:
                raise requests.RequestException("Temporary failure")
            return f"success with {arg1}, {arg2}, {kwarg1}"
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with patch('streamlit.warning'):  # Mock streamlit warning
                result = mock_api_function("test1", "test2", kwarg1="test3")
        
        assert result == "success with test1, test2, test3"
        assert len(call_args) == 2
        assert all(args == ("test1", "test2", "test3") for args in call_args)
    
    def test_retry_api_call_warning_messages(self):
        """Test that warning messages are displayed correctly."""
        @retry_api_call(max_retries=2, backoff_factor=0.5)
        def mock_api_function():
            raise requests.RequestException("Temporary failure")
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with patch('streamlit.warning') as mock_warning:
                with pytest.raises(requests.RequestException):
                    mock_api_function()
        
        # Should have called warning twice (for first and second retry)
        assert mock_warning.call_count == 2
        
        # Check warning message format
        call_args = [call[0][0] for call in mock_warning.call_args_list]
        assert "API call failed (attempt 1/3)" in call_args[0]
        assert "API call failed (attempt 2/3)" in call_args[1]
        assert "Retrying in" in call_args[0]
        assert "Retrying in" in call_args[1]
    
    def test_retry_api_call_random_jitter(self):
        """Test that random jitter is added to delay."""
        @retry_api_call(max_retries=1, backoff_factor=1.0)
        def mock_api_function():
            raise requests.RequestException("Temporary failure")
        
        # Mock random.uniform to return a specific value
        with patch('random.uniform', return_value=0.5):
            with patch('streamlit.warning'):  # Mock streamlit warning
                sleep_delays = []
                def mock_sleep(delay):
                    sleep_delays.append(delay)
                
                with patch('time.sleep', side_effect=mock_sleep):
                    with pytest.raises(requests.RequestException):
                        mock_api_function()
        
        # Check that jitter was added: backoff_factor * (2^0) + 0.5 = 1.0 + 0.5 = 1.5
        assert len(sleep_delays) == 1
        assert sleep_delays[0] == 1.5
    
    def test_retry_api_call_zero_retries(self):
        """Test behavior with zero retries configured."""
        call_count = 0
        
        @retry_api_call(max_retries=0, backoff_factor=0.1)
        def mock_api_function():
            nonlocal call_count
            call_count += 1
            raise requests.RequestException("Immediate failure")
        
        with pytest.raises(requests.RequestException):
            mock_api_function()
        
        assert call_count == 1  # Should only try once
    
    def test_retry_api_call_custom_backoff_factor(self):
        """Test retry with custom backoff factor."""
        @retry_api_call(max_retries=2, backoff_factor=2.0)
        def mock_api_function():
            raise requests.RequestException("Temporary failure")
        
        with patch('random.uniform', return_value=0.0):
            with patch('streamlit.warning'):  # Mock streamlit warning
                sleep_delays = []
                def mock_sleep(delay):
                    sleep_delays.append(delay)
                
                with patch('time.sleep', side_effect=mock_sleep):
                    with pytest.raises(requests.RequestException):
                        mock_api_function()
        
        # Check that custom backoff factor is used: 2.0 * (2^0) = 2.0, 2.0 * (2^1) = 4.0
        assert len(sleep_delays) == 2
        assert sleep_delays[0] == 2.0
        assert sleep_delays[1] == 4.0

@pytest.mark.integration
class TestRetryApiCallIntegration:
    """Integration tests for retry logic with mock APIs."""
    
    def test_retry_api_call_with_mock_openai_api(self, mock_openai_response):
        """Test retry logic with mock OpenAI API calls."""
        call_count = 0
        
        @retry_api_call(max_retries=2, backoff_factor=0.1)
        def mock_openai_call():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise openai.RateLimitError("Rate limit exceeded")
            return mock_openai_response
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with patch('streamlit.warning'):  # Mock streamlit warning
                result = mock_openai_call()
        
        assert result == mock_openai_response
        assert call_count == 2
    
    def test_retry_api_call_with_mock_http_requests(self):
        """Test retry logic with mock HTTP requests."""
        call_count = 0
        
        @retry_api_call(max_retries=2, backoff_factor=0.1)
        def mock_http_request():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise requests.ConnectionError("Connection timeout")
            return {"status": "success"}
        
        with patch('time.sleep'):  # Mock sleep to speed up test
            with patch('streamlit.warning'):  # Mock streamlit warning
                result = mock_http_request()
        
        assert result == {"status": "success"}
        assert call_count == 2
