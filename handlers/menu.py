from telebot import types


def send_support_menu(bot, chat_id):
    """Send the main support menu with all category buttons."""
    markup = types.InlineKeyboardMarkup(row_width=2)

    btn1 = types.InlineKeyboardButton("🔐 Login", callback_data="login")
    btn2 = types.InlineKeyboardButton("📚 Assessment", callback_data="assessment")
    btn3 = types.InlineKeyboardButton("📖 LMS", callback_data="lms")
    btn4 = types.InlineKeyboardButton("🧭 Navigation Help", callback_data="navhelp")
    btn5 = types.InlineKeyboardButton("❓ Other Issue", callback_data="other")
    btn6 = types.InlineKeyboardButton("💬 Chat with Us", callback_data="ai_chat")

    markup.add(btn1, btn2, btn3, btn4, btn5)
    markup.add(btn6)

    bot.send_message(chat_id, "Please select a category:", reply_markup=markup)

