"""Simple in-memory bot usage analytics."""
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class Analytics:
    """Tracks bot usage metrics in memory."""

    def __init__(self):
        self.total_messages = 0
        self.category_clicks = defaultdict(int)
        self.escalations = 0
        self.ai_queries = 0
        self.unique_users = set()

    def track_message(self, user_id):
        self.total_messages += 1
        self.unique_users.add(user_id)

    def track_category(self, category):
        self.category_clicks[category] += 1

    def track_escalation(self):
        self.escalations += 1

    def track_ai_query(self):
        self.ai_queries += 1

    def get_summary(self):
        header = (
            f"📊 **Bot Analytics**\n\n"
            f"• Total messages: {self.total_messages}\n"
            f"• Unique users: {len(self.unique_users)}\n"
            f"• AI queries: {self.ai_queries}\n"
            f"• Escalations: {self.escalations}\n"
        )
        if self.category_clicks:
            lines = "\n".join(
                f"• {k}: {v}"
                for k, v in sorted(self.category_clicks.items(), key=lambda x: -x[1])
            )
            return header + f"\n**Category Clicks:**\n{lines}"
        else:
            return header + "\nNo category data yet."


# Singleton
analytics = Analytics()
