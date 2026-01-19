from telebot import types


def register(bot):
    """Register Navigation Help callback handlers."""
    
    @bot.callback_query_handler(func=lambda call: call.data == "navhelp")
    def handle_navhelp(call):
        cid = call.message.chat.id

        bot.send_message(cid,
            "📱 **Navigation Help**\n\n"
            "I can guide you with:\n"
            "• Login\n• PCQ\n• Post Assessment\n• LMS Usage\n\n"
            "Tell me what you want help with.",
            parse_mode="Markdown"
        )
