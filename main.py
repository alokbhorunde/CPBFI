import os
import sys
import logging
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ----------------------------------------------------------
# LOGGING CONFIGURATION
# ----------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ----------------------------------------------------------
# ENVIRONMENT VALIDATION
# ----------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    logger.critical("BOT_TOKEN is not set in environment variables. Bot cannot start.")
    sys.exit(1)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY is not set — AI features will not work.")

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
if not all([SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
    logger.warning("Email env vars incomplete (SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL) — escalation emails will fail.")

bot = telebot.TeleBot(BOT_TOKEN)


from handlers import login, assessment, lms, navigation, other, ai_chat, photo, help, general, admin
from utils.health import start_health_server

# Callback handlers (button clicks)
login.register(bot)
assessment.register(bot)
lms.register(bot)
navigation.register(bot)
other.register(bot)
ai_chat.register(bot)

# Message handlers
admin.register(bot)     # Admin commands (/stats)
photo.register(bot)     # Photo handler
help.register(bot)      # Help command handler (groups + DMs)
general.register(bot)   # Catch-all for private messages (must be last!)


if __name__ == "__main__":
    logger.info("🤖 Bot is running...")
    logger.info("📁 Using modular handler structure")
    start_health_server(port=8080)
    try:
        bot.infinity_polling()
    except Exception as e:
        logger.critical(f"Bot crashed: {e}", exc_info=True)
        sys.exit(1)
