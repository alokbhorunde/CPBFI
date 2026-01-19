from telebot import types
from utils.ai import ask_ai_free
from handlers.menu import send_support_menu


# State for full AI chat mode
user_ai_chat_mode = {}


def register(bot):
    """Register AI Chat callback handlers."""
    
    @bot.callback_query_handler(func=lambda call: call.data in ["ai_chat", "exit_ai_chat"])
    def handle_ai_chat(call):
        cid = call.message.chat.id
        data = call.data

        if data == "ai_chat":
            user_ai_chat_mode[cid] = True

            exit_btn = types.InlineKeyboardMarkup()
            exit_btn.add(types.InlineKeyboardButton("❌ Exit AI Chat", callback_data="exit_ai_chat"))

            bot.send_message(cid,
                "💬 You are now chatting with the AI Assistant.\n"
                "Ask anything you want.\n\n"
                "Press 'Exit AI Chat' to return to menu.",
                reply_markup=exit_btn
            )

        elif data == "exit_ai_chat":
            user_ai_chat_mode[cid] = False
            bot.send_message(cid, "You have exited AI Chat.")
            send_support_menu(bot, cid)


def is_in_chat_mode(chat_id):
    """Check if user is in AI chat mode."""
    return user_ai_chat_mode.get(chat_id, False)


def handle_chat_message(bot, message):
    """Handle user message in AI chat mode."""
    cid = message.chat.id
    user_msg = message.text

    bot.send_chat_action(cid, "typing")
    ai_response = ask_ai_free(user_msg, human_mode=True)

    bot.send_message(cid, ai_response)
