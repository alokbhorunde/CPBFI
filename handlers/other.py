from telebot import types
from utils.ai import ask_ai_free


# State for "Other Issue" AI mode (one-shot)
user_ai_mode = {}


def register(bot):
    """Register Other Issue callback handlers."""
    
    @bot.callback_query_handler(func=lambda call: call.data == "other")
    def handle_other(call):
        cid = call.message.chat.id
        user_ai_mode[cid] = True
        
        bot.send_message(cid,
            "❓ Describe your issue.\n"
            "AI will analyze it and reply."
        )


def is_in_ai_mode(chat_id):
    """Check if user is in one-shot AI mode."""
    return user_ai_mode.get(chat_id, False)


def handle_ai_response(bot, message):
    """Handle user message with AI response (one-shot)."""
    cid = message.chat.id
    query = message.text

    bot.send_chat_action(cid, "typing")
    ai_reply = ask_ai_free(query)

    bot.send_message(cid, ai_reply)
    user_ai_mode[cid] = False  # Disable after 1 use
