"""
Pytest configuration and shared fixtures for Conference Research tests.
"""
import os
import tempfile
import pytest
import pandas as pd
from io import BytesIO
from pathlib import Path
from unittest.mock import Mock, patch
from typing import Dict, Any, List

# Set test environment
os.environ["ENVIRONMENT"] = "testing"
os.environ["CONFERENCE_RESEARCH_TESTING"] = "true"

@pytest.fixture(scope="session")
def test_data_dir():
    """Test data directory fixture."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture
def temp_dir():
    """Temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return pd.DataFrame({
        'Name': ['Dr. John Smith', 'Prof. Jane Doe', 'Dr. Alice Johnson'],
        'University': ['Harvard University', 'MIT', 'Stanford University'],
        'Email': ['john.smith@harvard.edu', '', 'alice@stanford.edu'],
        'Bio': ['', 'AI researcher', '']
    })

@pytest.fixture
def sample_xlsx_data():
    """Sample XLSX data for testing."""
    return pd.DataFrame({
        'Name': ['Dr. Bob Wilson', 'Prof. Carol White'],
        'Affiliation': ['Oxford University', 'Cambridge University'],
        'Research_Interest': ['Machine Learning', 'Quantum Computing']
    })

@pytest.fixture
def malicious_csv_data():
    """Malicious CSV data for security testing."""
    return pd.DataFrame({
        'Name': ['../../../etc/passwd', '<script>alert("xss")</script>'],
        'University': ['Evil University', 'Hack College']
    })

@pytest.fixture
def sample_csv_file(temp_dir, sample_csv_data):
    """Create a sample CSV file for testing."""
    file_path = temp_dir / "sample_data.csv"
    sample_csv_data.to_csv(file_path, index=False)
    return file_path

@pytest.fixture
def sample_xlsx_file(temp_dir, sample_xlsx_data):
    """Create a sample XLSX file for testing."""
    file_path = temp_dir / "sample_data.xlsx"
    sample_xlsx_data.to_excel(file_path, index=False)
    return file_path

@pytest.fixture
def large_csv_file(temp_dir):
    """Create a large CSV file for size testing."""
    file_path = temp_dir / "large_data.csv"
    # Create a file larger than 50MB
    large_data = pd.DataFrame({
        'Name': [f'Person {i}' for i in range(1000000)],
        'University': [f'University {i % 100}' for i in range(1000000)]
    })
    large_data.to_csv(file_path, index=False)
    return file_path

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response."""
    return {
        "choices": [{
            "message": {
                "content": "Dr. John Smith is a renowned researcher at Harvard University specializing in computer science. Email: john.smith@harvard.edu"
            }
        }],
        "usage": {
            "total_tokens": 50,
            "prompt_tokens": 30,
            "completion_tokens": 20
        }
    }

@pytest.fixture
def mock_serper_response():
    """Mock Google Serper API response."""
    return {
        "organic": [
            {
                "title": "Dr. John Smith - Harvard University",
                "link": "https://harvard.edu/profile/john-smith",
                "snippet": "Professor of Computer Science at Harvard University"
            }
        ]
    }

@pytest.fixture
def mock_web_content():
    """Mock web page content for scraping tests."""
    return """
    <html>
        <body>
            <h1>Dr. John Smith</h1>
            <p>Professor of Computer Science</p>
            <p>Email: john.smith@harvard.edu</p>
            <div>Research interests: Machine Learning, AI</div>
        </body>
    </html>
    """

@pytest.fixture
def mock_webdriver():
    """Mock Selenium WebDriver."""
    driver = Mock()
    driver.get.return_value = None
    driver.page_source = "<html><body>Test content</body></html>"
    driver.quit.return_value = None
    return driver

@pytest.fixture
def streamlit_app_config():
    """Mock Streamlit app configuration."""
    return {
        "openai_api_key": "test_openai_key",
        "serper_api_key": "test_serper_key",
        "max_file_size_mb": 50,
        "allowed_file_types": [".csv", ".xlsx", ".xls"]
    }

@pytest.fixture(autouse=True)
def mock_streamlit_secrets(streamlit_app_config):
    """Auto-mock Streamlit secrets for all tests."""
    with patch('streamlit.secrets', streamlit_app_config):
        yield streamlit_app_config

@pytest.fixture
def api_retry_config():
    """Configuration for API retry testing."""
    return {
        "max_attempts": 3,
        "initial_delay": 0.1,  # Faster for testing
        "backoff_factor": 2.0,
        "max_delay": 1.0
    }

@pytest.fixture
def file_validation_config():
    """Configuration for file validation testing."""
    return {
        "max_size_mb": 50,
        "allowed_extensions": [".csv", ".xlsx", ".xls"],
        "allowed_mime_types": [
            "text/csv",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "application/vnd.ms-excel"
        ]
    }

class MockResponse:
    """Mock HTTP response for testing."""
    def __init__(self, json_data=None, text_data=None, status_code=200, headers=None):
        self.json_data = json_data
        self.text_data = text_data
        self.status_code = status_code
        self.headers = headers or {}
        self.ok = status_code < 400

    def json(self):
        if self.json_data is None:
            raise ValueError("No JSON data")
        return self.json_data

    @property
    def text(self):
        return self.text_data or ""

    def raise_for_status(self):
        if not self.ok:
            raise requests.exceptions.HTTPError(f"HTTP {self.status_code}")

@pytest.fixture
def mock_requests_get():
    """Mock requests.get for HTTP testing."""
    with patch('requests.get') as mock_get:
        yield mock_get

@pytest.fixture
def mock_requests_post():
    """Mock requests.post for HTTP testing."""
    with patch('requests.post') as mock_post:
        yield mock_post

# Test markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require API access"
    )
    config.addinivalue_line(
        "markers", "webdriver: marks tests that require WebDriver"
    )
