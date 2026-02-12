"""Tests for AI response function."""
from unittest.mock import patch, MagicMock
from utils.ai import ask_ai_free


class TestAskAiFree:
    @patch("utils.ai.groq_client")
    def test_returns_response(self, mock_client):
        mock_choice = MagicMock()
        mock_choice.message.content = "Try clearing your cache."
        mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

        result = ask_ai_free("I can't login")
        assert result == "Try clearing your cache."

    @patch("utils.ai.groq_client")
    def test_empty_prompt_returns_fallback(self, mock_client):
        mock_choice = MagicMock()
        mock_choice.message.content = "Please provide more details."
        mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

        result = ask_ai_free("")
        assert result is not None

    @patch("utils.ai.groq_client")
    def test_none_prompt_returns_fallback(self, mock_client):
        mock_choice = MagicMock()
        mock_choice.message.content = "Please provide more details."
        mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])

        result = ask_ai_free(None)
        assert result is not None

    @patch("utils.ai.groq_client")
    def test_api_error_returns_fallback(self, mock_client):
        mock_client.chat.completions.create.side_effect = Exception("API down")
        result = ask_ai_free("test query")
        assert "unavailable" in result.lower() or "try again" in result.lower()
