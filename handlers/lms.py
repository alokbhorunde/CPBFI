from telebot import types


def register(bot):
    """Register LMS-related callback handlers."""
    
    @bot.callback_query_handler(func=lambda call: call.data == "lms")
    def handle_lms(call):
        cid = call.message.chat.id

        bot.send_message(cid,
            "📘 **LMS Help**\n"
            "Try:\n• Refresh dashboard\n• Clear cache\n• Try another browser/device\n\n"
            "If still stuck, share details or screenshot.",
            parse_mode="Markdown"
        )
