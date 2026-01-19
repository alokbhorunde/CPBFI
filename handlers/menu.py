from telebot import types


def send_support_menu(bot, chat_id):
    """Send the main support menu with all category buttons."""
    markup = types.InlineKeyboardMarkup(row_width=2)

    btn1 = types.InlineKeyboardButton(" Login", callback_data="login")
    btn2 = types.InlineKeyboardButton(" PCQ", callback_data="pcq")
    btn3 = types.InlineKeyboardButton(" Post Assessment", callback_data="post")
    btn4 = types.InlineKeyboardButton(" LMS", callback_data="lms")
    btn5 = types.InlineKeyboardButton(" Navigation Help", callback_data="navhelp")
    btn6 = types.InlineKeyboardButton(" Other Issue", callback_data="other")
    btn7 = types.InlineKeyboardButton("💬 Chat with Us", callback_data="ai_chat")

    markup.add(btn1, btn2, btn3, btn4, btn5, btn6)
    markup.add(btn7)

    bot.send_message(chat_id, "Please select a category:", reply_markup=markup)
