from telebot import types


def register(bot):
    """Register all login-related callback handlers."""
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("login"))
    def handle_login(call):
        cid = call.message.chat.id
        data = call.data

        if data == "login":
            markup = types.InlineKeyboardMarkup()
            yes = types.InlineKeyboardButton("✔ Yes, It's Fixed", callback_data="login_fixed")
            no = types.InlineKeyboardButton("➡ Next Step", callback_data="login_step2")
            markup.add(yes, no)

            bot.send_message(cid,
                "🔐 **Login Help — Step 1**\n\n"
                "• Check your internet connection\n"
                "• Switch between WiFi ↔ Mobile Data\n\n"
                "Did it work?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "login_step2":
            markup = types.InlineKeyboardMarkup()
            yes = types.InlineKeyboardButton("✔ Fixed", callback_data="login_fixed")
            no = types.InlineKeyboardButton("➡ Next Step", callback_data="login_step3")
            markup.add(yes, no)

            bot.send_message(cid,
                "🔐 **Login Help — Step 2**\n"
                "• Clear browser cache\n"
                "• Try Incognito Mode\n\n"
                "Did this help?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "login_step3":
            bot.send_message(cid,
                "🔐 **Login Help — Step 3**\n"
                "Try:\n• Another browser\n• Another device\n\n"
                "If still stuck, explain your issue or send a screenshot.",
                parse_mode="Markdown"
            )

        elif data == "login_fixed":
            bot.send_message(cid, "🎉 Great! Your login issue is resolved.")
