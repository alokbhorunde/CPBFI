import os
import telebot
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ----------------------------------------------------------
# BOT INITIALIZATION
# ----------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)

# ----------------------------------------------------------
# REGISTER ALL HANDLERS
# Order matters! More specific handlers should be registered first
# ----------------------------------------------------------
from handlers import login, assessment, lms, navigation, other, ai_chat, photo, help, general

# Callback handlers (button clicks)
login.register(bot)
assessment.register(bot)
lms.register(bot)
navigation.register(bot)
other.register(bot)
ai_chat.register(bot)

# Message handlers
photo.register(bot)     # Photo handler
help.register(bot)      # Help command handler (groups + DMs)
general.register(bot)   # Catch-all for private messages (must be last!)

# ----------------------------------------------------------
# RUN BOT
# ----------------------------------------------------------
if __name__ == "__main__":
    print("🤖 Bot is running...")
    print("📁 Using modular handler structure")
    bot.infinity_polling()
