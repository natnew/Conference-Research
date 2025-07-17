"""
Unit tests for file validation functionality in BioGen.py
"""
import pytest
import pandas as pd
from io import BytesIO
from unittest.mock import Mock, MagicMock
import sys
import os

# Add the project root to the path so we can import from BioGen
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from BioGen import validate_file_upload
except ImportError:
    # Mock the function if import fails during test discovery
    def validate_file_upload(uploaded_file):
        return True, "Mock validation"

class MockUploadedFile:
    """Mock Streamlit UploadedFile for testing."""
    
    def __init__(self, name, size, file_type, content=None):
        self.name = name
        self.size = size
        self.type = file_type
        self.content = content or b"test content"
    
    def read(self):
        return self.content
    
    def seek(self, position):
        pass

@pytest.mark.unit
class TestFileValidation:
    """Test cases for file upload validation."""
    
    def test_validate_file_upload_none_file(self):
        """Test validation with None file."""
        is_valid, message = validate_file_upload(None)
        assert not is_valid
        assert "No file uploaded" in message
    
    def test_validate_file_upload_valid_csv(self):
        """Test validation with valid CSV file."""
        mock_file = MockUploadedFile(
            name="test_data.csv",
            size=1024,  # 1KB
            file_type="text/csv"
        )
        
        is_valid, message = validate_file_upload(mock_file)
        assert is_valid
        assert "File validation passed" in message
    
    def test_validate_file_upload_valid_xlsx(self):
        """Test validation with valid XLSX file."""
        mock_file = MockUploadedFile(
            name="test_data.xlsx",
            size=2048,  # 2KB
            file_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        is_valid, message = validate_file_upload(mock_file)
        assert is_valid
        assert "File validation passed" in message
    
    def test_validate_file_upload_valid_xls(self):
        """Test validation with valid XLS file."""
        mock_file = MockUploadedFile(
            name="test_data.xls",
            size=1536,  # 1.5KB
            file_type="application/vnd.ms-excel"
        )
        
        is_valid, message = validate_file_upload(mock_file)
        assert is_valid
        assert "File validation passed" in message
    
    def test_validate_file_upload_oversized_file(self):
        """Test validation with file exceeding size limit."""
        oversized_file = MockUploadedFile(
            name="large_file.csv",
            size=60 * 1024 * 1024,  # 60MB
            file_type="text/csv"
        )
        
        is_valid, message = validate_file_upload(oversized_file)
        assert not is_valid
        assert "exceeds maximum allowed size" in message
        assert "60.0MB" in message
    
    def test_validate_file_upload_invalid_extension(self):
        """Test validation with unsupported file extension."""
        invalid_file = MockUploadedFile(
            name="test_data.txt",
            size=1024,
            file_type="text/plain"
        )
        
        is_valid, message = validate_file_upload(invalid_file)
        assert not is_valid
        assert "File type '.txt' not allowed" in message
        assert "Supported formats:" in message
    
    def test_validate_file_upload_suspicious_filename_path_traversal(self):
        """Test validation with path traversal attack in filename."""
        malicious_file = MockUploadedFile(
            name="../../../etc/passwd.csv",
            size=1024,
            file_type="text/csv"
        )
        
        is_valid, message = validate_file_upload(malicious_file)
        assert not is_valid
        assert "File name contains invalid characters" in message
    
    def test_validate_file_upload_suspicious_filename_special_chars(self):
        """Test validation with special characters in filename."""
        suspicious_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        
        for char in suspicious_chars:
            malicious_file = MockUploadedFile(
                name=f"test{char}file.csv",
                size=1024,
                file_type="text/csv"
            )
            
            is_valid, message = validate_file_upload(malicious_file)
            assert not is_valid
            assert "File name contains invalid characters" in message
    
    def test_validate_file_upload_mime_type_mismatch_csv(self):
        """Test validation with MIME type mismatch for CSV."""
        # This should trigger a warning but still pass validation
        mismatched_file = MockUploadedFile(
            name="test_data.csv",
            size=1024,
            file_type="application/octet-stream"  # Wrong MIME type
        )
        
        # The function should still pass but with a warning
        is_valid, message = validate_file_upload(mismatched_file)
        assert is_valid  # Should still pass validation
    
    def test_validate_file_upload_edge_case_max_size(self):
        """Test validation with file at exact size limit."""
        max_size_file = MockUploadedFile(
            name="max_size.csv",
            size=50 * 1024 * 1024,  # Exactly 50MB
            file_type="text/csv"
        )
        
        is_valid, message = validate_file_upload(max_size_file)
        assert is_valid
        assert "File validation passed" in message
    
    def test_validate_file_upload_edge_case_just_over_limit(self):
        """Test validation with file just over size limit."""
        over_limit_file = MockUploadedFile(
            name="over_limit.csv",
            size=50 * 1024 * 1024 + 1,  # 1 byte over 50MB
            file_type="text/csv"
        )
        
        is_valid, message = validate_file_upload(over_limit_file)
        assert not is_valid
        assert "exceeds maximum allowed size" in message
    
    def test_validate_file_upload_empty_filename(self):
        """Test validation with empty filename."""
        empty_name_file = MockUploadedFile(
            name="",
            size=1024,
            file_type="text/csv"
        )
        
        # This should fail due to extension check
        is_valid, message = validate_file_upload(empty_name_file)
        assert not is_valid
    
    def test_validate_file_upload_no_extension(self):
        """Test validation with filename without extension."""
        no_ext_file = MockUploadedFile(
            name="testfile",
            size=1024,
            file_type="text/csv"
        )
        
        is_valid, message = validate_file_upload(no_ext_file)
        assert not is_valid
        assert "not allowed" in message
    
    def test_validate_file_upload_case_insensitive_extension(self):
        """Test validation with uppercase file extension."""
        uppercase_ext_file = MockUploadedFile(
            name="test_data.CSV",
            size=1024,
            file_type="text/csv"
        )
        
        is_valid, message = validate_file_upload(uppercase_ext_file)
        assert is_valid
        assert "File validation passed" in message
    
    def test_validate_file_upload_multiple_dots_in_filename(self):
        """Test validation with multiple dots in filename."""
        multi_dot_file = MockUploadedFile(
            name="test.data.backup.csv",
            size=1024,
            file_type="text/csv"
        )
        
        is_valid, message = validate_file_upload(multi_dot_file)
        assert is_valid
        assert "File validation passed" in message

@pytest.mark.integration
class TestFileValidationIntegration:
    """Integration tests for file validation with real file-like objects."""
    
    def test_validate_file_upload_with_real_csv_content(self, sample_csv_data):
        """Test validation with real CSV content."""
        # Convert DataFrame to CSV bytes
        csv_buffer = BytesIO()
        sample_csv_data.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue()
        
        mock_file = MockUploadedFile(
            name="real_data.csv",
            size=len(csv_bytes),
            file_type="text/csv",
            content=csv_bytes
        )
        
        is_valid, message = validate_file_upload(mock_file)
        assert is_valid
        assert "File validation passed" in message
    
    def test_validate_file_upload_with_malicious_content(self, malicious_csv_data):
        """Test validation with potentially malicious CSV content."""
        # Convert DataFrame to CSV bytes
        csv_buffer = BytesIO()
        malicious_csv_data.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue()
        
        # The file validation should pass (content validation is separate)
        mock_file = MockUploadedFile(
            name="clean_filename.csv",
            size=len(csv_bytes),
            file_type="text/csv",
            content=csv_bytes
        )
        
        is_valid, message = validate_file_upload(mock_file)
        assert is_valid  # File validation should pass, content validation is separate
    
    @pytest.mark.parametrize("file_extension,mime_type", [
        (".csv", "text/csv"),
        (".xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
        (".xls", "application/vnd.ms-excel"),
    ])
    def test_validate_file_upload_supported_formats(self, file_extension, mime_type):
        """Test validation with all supported file formats."""
        mock_file = MockUploadedFile(
            name=f"test{file_extension}",
            size=1024,
            file_type=mime_type
        )
        
        is_valid, message = validate_file_upload(mock_file)
        assert is_valid
        assert "File validation passed" in message
