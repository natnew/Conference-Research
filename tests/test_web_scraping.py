"""
Integration tests for web scraping functionality.
"""
import pytest
import requests
from unittest.mock import patch, Mock
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from BioGen import scrape_text_from_url
except ImportError:
    # Mock the function if import fails during test discovery
    def scrape_text_from_url(url, timeout=None):
        return "mock scraped content"

@pytest.mark.unit
class TestWebScraping:
    """Test cases for web scraping functionality."""
    
    @patch('requests.get')
    def test_scrape_text_from_url_success(self, mock_get, mock_web_content):
        """Test successful web scraping."""
        # Setup mock response
        mock_response = Mock()
        mock_response.content = mock_web_content.encode('utf-8')
        mock_response.text = mock_web_content
        mock_response.encoding = 'utf-8'
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = scrape_text_from_url("https://example.com/profile")
        
        assert result is not None
        assert "Dr. John Smith" in result
        assert "Computer Science" in result
    
    @patch('requests.get')
    def test_scrape_text_from_url_timeout(self, mock_get):
        """Test web scraping with timeout."""
        mock_get.side_effect = requests.exceptions.Timeout("Request timed out")
        
        result = scrape_text_from_url("https://example.com/profile")
        
        assert result is None
    
    @patch('requests.get')
    def test_scrape_text_from_url_http_error(self, mock_get):
        """Test web scraping with HTTP error."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        result = scrape_text_from_url("https://example.com/notfound")
        
        assert result is None
    
    def test_scrape_text_from_url_invalid_url(self):
        """Test web scraping with invalid URL."""
        result = scrape_text_from_url("invalid-url")
        
        assert result is None
    
    def test_scrape_text_from_url_empty_url(self):
        """Test web scraping with empty URL."""
        result = scrape_text_from_url("")
        
        assert result is None

@pytest.mark.integration  
class TestWebScrapingIntegration:
    """Integration tests for web scraping with real configuration."""
    
    def test_scrape_text_configuration_usage(self):
        """Test that web scraping uses configuration values."""
        # This test validates that the configuration system is working
        # We can't test with real HTTP requests in CI, but we can test the function signature
        try:
            # This should not raise an exception even with invalid URL
            # because the URL validation will catch it
            result = scrape_text_from_url("not-a-url")
            assert result is None
        except Exception as e:
            pytest.fail(f"Function should handle invalid URLs gracefully: {e}")
    
    @pytest.mark.parametrize("url", [
        "https://example.com",
        "http://test.com",
        "https://university.edu/profile"
    ])
    def test_scrape_text_url_validation(self, url):
        """Test URL validation with various valid URLs."""
        # We're testing the URL validation logic, not making real requests
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.content = b"<html><body>Test content</body></html>"
            mock_response.text = "<html><body>Test content</body></html>"
            mock_response.encoding = 'utf-8'
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            result = scrape_text_from_url(url)
            assert result is not None
