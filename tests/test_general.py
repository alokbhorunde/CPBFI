"""Tests for greeting detection and state routing."""
from handlers.general import is_greeting, GREETING_KEYWORDS


class TestGreeting:
    def test_all_keywords_detected(self):
        for kw in GREETING_KEYWORDS:
            assert is_greeting(kw) is True, f"Failed for keyword: {kw}"

    def test_case_insensitive(self):
        assert is_greeting("HI") is True
        assert is_greeting("Hello") is True
        assert is_greeting("MENU") is True

    def test_with_whitespace(self):
        assert is_greeting("  hi  ") is True
        assert is_greeting("  hello ") is True

    def test_start_command(self):
        assert is_greeting("/start") is True
        assert is_greeting("/start@botname") is True

    def test_non_greetings(self):
        assert is_greeting("how are you") is False
        assert is_greeting("login issue") is False
        assert is_greeting("") is False
