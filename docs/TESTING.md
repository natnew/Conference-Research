# Testing Guide for Conference Research Application

This guide explains how to run tests, write new tests, and maintain the testing infrastructure for the Conference Research application.

## Quick Start

```bash
# Set up development environment
python scripts/make.py install

# Run all tests
python scripts/make.py test

# Run tests without coverage (faster)
python scripts/make.py test-fast

# Run only unit tests
python scripts/make.py test-unit

# Run only integration tests
python scripts/make.py test-integration
```

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures and configuration
├── test_file_validation.py        # File upload validation tests
├── test_retry_logic.py            # API retry mechanism tests
├── test_web_scraping.py           # Web scraping functionality tests
├── test_bio_generation.py         # Bio generation tests (planned)
├── fixtures/                      # Test data files
├── mocks/                         # Mock services and responses
└── integration/                   # Integration test files
```

## Test Types

### Unit Tests
- Test individual functions in isolation
- Use mocks for external dependencies
- Fast execution (< 1 second per test)
- Run with: `pytest -m unit`

### Integration Tests  
- Test component interactions
- May use real APIs in development
- Slower execution (1-10 seconds per test)
- Run with: `pytest -m integration`

### End-to-End Tests
- Test complete workflows
- Use real or staging environments
- Slowest execution (10+ seconds per test)
- Run with: `pytest -m e2e`

## Writing Tests

### Basic Test Structure

```python
import pytest
from unittest.mock import Mock, patch

@pytest.mark.unit
class TestMyFunction:
    """Test cases for my_function."""
    
    def test_success_case(self):
        """Test successful execution."""
        result = my_function("test_input")
        assert result == "expected_output"
    
    def test_error_case(self):
        """Test error handling."""
        with pytest.raises(ValueError):
            my_function("invalid_input")
```

### Using Fixtures

```python
def test_with_sample_data(sample_csv_data):
    """Test using predefined sample data."""
    assert len(sample_csv_data) == 3
    assert "Name" in sample_csv_data.columns
```

### Mocking External Services

```python
@patch('requests.get')
def test_api_call(mock_get):
    """Test API call with mocked response."""
    mock_get.return_value.json.return_value = {"status": "success"}
    result = api_function()
    assert result["status"] == "success"
```

## Test Configuration

### Environment Variables
Set these environment variables for testing:
```bash
ENVIRONMENT=testing
CONFERENCE_RESEARCH_TESTING=true
OPENAI_API_KEY=test_key_here
SERPER_API_KEY=test_key_here
```

### Test-Specific Settings
Tests use the `config/testing.yaml` configuration:
- Shorter timeouts for faster test execution
- Minimal retry attempts 
- Stricter validation for security testing
- Disabled analytics and caching

## Coverage Requirements

- **Minimum 70% overall coverage** required for CI to pass
- **90%+ coverage for security functions** (file validation, API retry)
- **All exception handling paths** must be tested

### Viewing Coverage Reports

```bash
# Generate HTML coverage report
python scripts/make.py test

# Open coverage report
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

## Continuous Integration

Tests run automatically on:
- Push to main/develop branches
- Pull requests to main
- Multiple OS: Ubuntu, Windows, macOS
- Multiple Python versions: 3.9, 3.10, 3.11

### CI Configuration
See `.github/workflows/test.yml` for full CI pipeline including:
- Dependency caching
- Security scanning
- Code formatting checks
- Type checking
- Test execution with coverage

## Mock Testing Best Practices

### File Upload Mocking
```python
class MockUploadedFile:
    def __init__(self, name, size, file_type, content=None):
        self.name = name
        self.size = size
        self.type = file_type
        self.content = content or b"test content"

def test_file_validation():
    mock_file = MockUploadedFile("test.csv", 1024, "text/csv")
    is_valid, message = validate_file_upload(mock_file)
    assert is_valid
```

### API Response Mocking
```python
@pytest.fixture
def mock_openai_response():
    return {
        "choices": [{
            "message": {
                "content": "Generated biography text here"
            }
        }],
        "usage": {"total_tokens": 50}
    }
```

## Debugging Tests

### Running Specific Tests
```bash
# Run specific test file
pytest tests/test_file_validation.py -v

# Run specific test class
pytest tests/test_file_validation.py::TestFileValidation -v

# Run specific test method
pytest tests/test_file_validation.py::TestFileValidation::test_validate_file_upload_none_file -v
```

### Debug Output
```bash
# Show print statements
pytest -s

# Show detailed output
pytest -v --tb=long

# Stop on first failure
pytest -x
```

### Using Debugger
```python
def test_debug_example():
    import pdb; pdb.set_trace()  # Set breakpoint
    result = function_to_debug()
    assert result == expected
```

## Common Test Patterns

### Testing Configuration
```python
def test_configuration_loading():
    """Test that configuration loads correctly."""
    config = get_config()
    assert config.api.openai_model == "gpt-4o-mini-2024-07-18"
    assert config.file_upload.max_size_mb > 0
```

### Testing Retry Logic
```python
def test_retry_mechanism():
    """Test API retry with exponential backoff."""
    call_count = 0
    
    @retry_api_call(max_retries=2)
    def failing_function():
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise requests.RequestException("Temporary failure")
        return "success"
    
    result = failing_function()
    assert result == "success"
    assert call_count == 2
```

### Testing File Validation
```python
def test_file_security():
    """Test security validation for malicious files."""
    malicious_file = MockUploadedFile(
        "../../../etc/passwd", 1024, "text/csv"
    )
    is_valid, message = validate_file_upload(malicious_file)
    assert not is_valid
    assert "invalid characters" in message
```

## Test Data Management

### Sample Data Files
- `tests/fixtures/sample_data.csv` - Clean test data
- `tests/fixtures/malicious_file.csv` - Security test data
- `tests/fixtures/large_file.csv` - Performance test data

### Data Generation
```python
@pytest.fixture
def large_dataset():
    """Generate large dataset for performance testing."""
    return pd.DataFrame({
        'Name': [f'Person {i}' for i in range(10000)],
        'University': [f'University {i % 100}' for i in range(10000)]
    })
```

## Performance Testing

### Timing Tests
```python
import time

def test_performance():
    """Test that function completes within time limit."""
    start_time = time.time()
    result = expensive_function()
    end_time = time.time()
    
    assert result is not None
    assert (end_time - start_time) < 5.0  # Must complete in under 5 seconds
```

### Memory Usage
```python
import psutil
import os

def test_memory_usage():
    """Test that function doesn't leak memory."""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    for _ in range(1000):
        result = function_under_test()
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # Allow some memory increase but not excessive
    assert memory_increase < 50 * 1024 * 1024  # Less than 50MB increase
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure the project is installed in development mode
   pip install -e .
   ```

2. **Configuration Errors**
   ```bash
   # Check environment variables
   echo $ENVIRONMENT
   echo $CONFERENCE_RESEARCH_TESTING
   ```

3. **Test Discovery Issues**
   ```bash
   # Check test file naming (must start with test_ or end with _test.py)
   # Check test function naming (must start with test_)
   ```

4. **Fixture Not Found**
   ```python
   # Ensure fixtures are defined in conftest.py or imported properly
   # Check fixture scope (function, class, module, session)
   ```

### Getting Help

- Check test output for detailed error messages
- Use `pytest --collect-only` to see discovered tests
- Run with `-v` flag for verbose output
- Check the CI logs for environment-specific issues

## Contributing Tests

When adding new features:

1. **Write tests first** (TDD approach recommended)
2. **Include both success and failure cases**
3. **Test edge cases and boundary conditions**
4. **Add appropriate test markers** (`@pytest.mark.unit`, etc.)
5. **Update documentation** if adding new test patterns
6. **Ensure tests pass locally** before pushing

### Test Review Checklist

- [ ] Tests cover new functionality
- [ ] Tests include error cases
- [ ] Mocks are used appropriately
- [ ] Test names are descriptive
- [ ] Assertions are meaningful
- [ ] Tests are fast and reliable
- [ ] Coverage meets requirements
