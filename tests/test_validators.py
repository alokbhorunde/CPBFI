"""Tests for email validation."""
import pytest
from utils.validators import is_valid_email


class TestEmailValidation:
    def test_valid_emails(self):
        assert is_valid_email("user@example.com") is True
        assert is_valid_email("test.name@domain.org") is True
        assert is_valid_email("user+tag@gmail.com") is True
        assert is_valid_email("a@b.co") is True

    def test_invalid_emails(self):
        assert is_valid_email("notanemail") is False
        assert is_valid_email("@domain.com") is False
        assert is_valid_email("user@") is False
        assert is_valid_email("user @domain.com") is False
        assert is_valid_email("") is False

    def test_edge_cases(self):
        assert is_valid_email("user@domain.c") is False
        assert is_valid_email("user@.com") is False
        assert is_valid_email("user@domain..com") is False
