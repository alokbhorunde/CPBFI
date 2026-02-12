"""Admin-only commands for monitoring bot usage."""
import os
import logging
from utils.analytics import analytics

logger = logging.getLogger(__name__)

# Load admin IDs from .env (comma-separated)
ADMIN_IDS = []
admin_ids_str = os.getenv("ADMIN_IDS", "")
if admin_ids_str:
    ADMIN_IDS = [int(x.strip()) for x in admin_ids_str.split(",") if x.strip().isdigit()]


def register(bot):
    """Register admin command handlers."""

    @bot.message_handler(commands=["stats"])
    def stats_handler(message):
        user_id = message.from_user.id

        if not ADMIN_IDS:
            logger.warning(f"ADMIN_IDS not configured. User {user_id} tried /stats.")
            return

        if user_id not in ADMIN_IDS:
            logger.warning(f"Unauthorized /stats attempt by user {user_id}")
            return

        summary = analytics.get_summary()
        bot.send_message(message.chat.id, summary, parse_mode="Markdown")
        logger.info(f"Admin {user_id} viewed stats")
