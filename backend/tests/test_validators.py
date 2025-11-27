"""Unit tests for validation functions."""

import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'message_printer_api'))

from chalicelib import validators


class TestValidateName:
    """Tests for validate_name function."""
    
    def test_valid_name(self):
        """Test that valid name passes validation."""
        result = validators.validate_name("John")
        assert result == "John"
    
    def test_name_with_whitespace_trimmed(self):
        """Test that name is trimmed of leading/trailing whitespace."""
        result = validators.validate_name("  John Doe  ")
        assert result == "John Doe"
    
    def test_none_name_raises_error(self):
        """Test that None name raises ValueError."""
        with pytest.raises(ValueError, match="Name is required"):
            validators.validate_name(None)
    
    def test_empty_name_raises_error(self):
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validators.validate_name("")
    
    def test_whitespace_only_name_raises_error(self):
        """Test that whitespace-only name raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validators.validate_name("   ")
    
    def test_name_exactly_50_chars_valid(self):
        """Test that name with exactly 50 characters is valid."""
        name = "a" * 50
        result = validators.validate_name(name)
        assert result == name
        assert len(result) == 50
    
    def test_name_51_chars_raises_error(self):
        """Test that name over 50 characters raises ValueError."""
        name = "a" * 51
        with pytest.raises(ValueError, match="too long"):
            validators.validate_name(name)
    
    def test_name_with_special_characters(self):
        """Test that name with special characters is handled correctly."""
        result = validators.validate_name("María José")
        assert result == "María José"


class TestValidateMessageContent:
    """Tests for validate_message_content function."""
    
    def test_valid_content(self):
        """Test that valid content passes validation."""
        result = validators.validate_message_content("Hello, world!")
        assert result == "Hello, world!"
    
    def test_content_with_whitespace_trimmed(self):
        """Test that content is trimmed of leading/trailing whitespace."""
        result = validators.validate_message_content("  Hello  ")
        assert result == "Hello"
    
    def test_none_content_raises_error(self):
        """Test that None content raises ValueError."""
        with pytest.raises(ValueError, match="Content is required"):
            validators.validate_message_content(None)
    
    def test_empty_content_raises_error(self):
        """Test that empty content raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validators.validate_message_content("")
    
    def test_whitespace_only_raises_error(self):
        """Test that whitespace-only content raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validators.validate_message_content("   ")
    
    def test_content_exactly_280_chars_valid(self):
        """Test that content with exactly 280 characters is valid."""
        content = "a" * 280
        result = validators.validate_message_content(content)
        assert result == content
        assert len(result) == 280
    
    def test_content_281_chars_raises_error(self):
        """Test that content over 280 characters raises ValueError."""
        content = "a" * 281
        with pytest.raises(ValueError, match="too long"):
            validators.validate_message_content(content)
    
    def test_content_with_unicode(self):
        """Test that unicode content is handled correctly."""
        result = validators.validate_message_content("Hello 👋 世界")
        assert result == "Hello 👋 世界"


class TestValidateMessageId:
    """Tests for validate_message_id function."""
    
    def test_valid_id(self):
        """Test that valid ID passes validation."""
        result = validators.validate_message_id("12345")
        assert result == "12345"
    
    def test_uuid_format_id(self):
        """Test that UUID format ID passes validation."""
        uuid = "550e8400-e29b-41d4-a716-446655440000"
        result = validators.validate_message_id(uuid)
        assert result == uuid
    
    def test_id_with_whitespace_trimmed(self):
        """Test that ID is trimmed of leading/trailing whitespace."""
        result = validators.validate_message_id("  12345  ")
        assert result == "12345"
    
    def test_none_id_raises_error(self):
        """Test that None ID raises ValueError."""
        with pytest.raises(ValueError, match="ID is required"):
            validators.validate_message_id(None)
    
    def test_empty_id_raises_error(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validators.validate_message_id("")
    
    def test_whitespace_only_id_raises_error(self):
        """Test that whitespace-only ID raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            validators.validate_message_id("   ")

