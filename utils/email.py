import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


def send_email_to_it(user, issue):
    """Send email notification to IT team. Returns True if sent, False if failed."""
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL")

    if not all([sender_email, sender_password, receiver_email]):
        logger.error("Email config missing: SENDER_EMAIL, SENDER_PASSWORD, or RECEIVER_EMAIL not set")
        return False

    smtp_server = "smtp.gmail.com"
    port = 587

    subject = f"CRITICAL ISSUE: {issue.upper()}"
    body = f"""
A critical issue was detected.

User: {user}
Issue Category: {issue}

Please check the problem immediately.
"""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, port, timeout=10)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        logger.info(f"Email sent successfully for user: {user}")
        return True
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return False
