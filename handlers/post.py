from telebot import types


def register(bot):
    """Register all Post Assessment-related callback handlers."""
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("post"))
    def handle_post(call):
        cid = call.message.chat.id
        data = call.data

        if data == "post":
            markup = types.InlineKeyboardMarkup()
            yes = types.InlineKeyboardButton("✔ Fixed", callback_data="post_fixed")
            no = types.InlineKeyboardButton("➡ Next Step", callback_data="post_step2")
            markup.add(yes, no)

            bot.send_message(cid,
                "🧪 **Post Assessment — Step 1**\n"
                "Refresh the page and try again.\n\n"
                "Did it work?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "post_step2":
            bot.send_message(cid,
                "🧪 **Post Assessment — Step 2**\n"
                "Check if your **assessment time window is active**.\n"
                "You can only attempt within the allowed time.\n\n"
                "If still stuck, describe your issue.",
                parse_mode="Markdown"
            )

        elif data == "post_fixed":
            bot.send_message(cid, "🎉 Your assessment issue is resolved.")
