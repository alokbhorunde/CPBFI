"""Tests for email sending."""
from unittest.mock import patch, MagicMock
from utils.email import send_email_to_it


class TestSendEmail:
    @patch.dict("os.environ", {
        "SENDER_EMAIL": "test@gmail.com",
        "SENDER_PASSWORD": "password123",
        "RECEIVER_EMAIL": "support@cpbfi.org"
    })
    @patch("utils.email.smtplib.SMTP")
    def test_successful_send(self, mock_smtp):
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server

        result = send_email_to_it("John Doe (john@test.com)", "Login - Invalid Credentials")
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()

    @patch.dict("os.environ", {
        "SENDER_EMAIL": "test@gmail.com",
        "SENDER_PASSWORD": "password123",
        "RECEIVER_EMAIL": "support@cpbfi.org"
    })
    @patch("utils.email.smtplib.SMTP")
    def test_smtp_failure(self, mock_smtp):
        mock_smtp.side_effect = Exception("Connection refused")
        result = send_email_to_it("John Doe", "Login Issue")
        assert result is False

    @patch.dict("os.environ", {
        "SENDER_EMAIL": "",
        "SENDER_PASSWORD": "",
        "RECEIVER_EMAIL": ""
    })
    def test_missing_config(self):
        result = send_email_to_it("John Doe", "Login Issue")
        assert result is False
