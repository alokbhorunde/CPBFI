from telebot import types
from utils.ai import ask_ai_free
from handlers.menu import send_support_menu

user_ai_mode = {}


def register(bot):
    """Register Other Issue callback handlers."""

    @bot.callback_query_handler(func=lambda call: call.data in ["other", "other_resolved", "other_back_menu"])
    def handle_other(call):
        bot.answer_callback_query(call.id)
        cid = call.message.chat.id

        if call.data == "other_resolved":
            bot.send_message(cid, "Great! Glad your issue was resolved.\n\nHappy learning!")
            send_support_menu(bot, cid)
            return

        if call.data == "other_back_menu":
            send_support_menu(bot, cid)
            return

        user_ai_mode[cid] = True

        bot.send_message(cid,
            "Describe your issue.\n"
            "AI will analyze it and reply."
        )


def is_in_ai_mode(chat_id):
    return user_ai_mode.get(chat_id, False)


def handle_ai_response(bot, message):
    cid = message.chat.id
    query = message.text

    bot.send_chat_action(cid, "typing")
    ai_reply = ask_ai_free(query)

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Issue Resolved", callback_data="other_resolved"),
        types.InlineKeyboardButton("Still Need Help", callback_data="other")
    )
    markup.add(
        types.InlineKeyboardButton("⬅️ Main Menu", callback_data="other_back_menu")
    )

    bot.send_message(cid, ai_reply, reply_markup=markup, parse_mode="Markdown")
    user_ai_mode[cid] = False


def handle_other_resolved(bot, cid):
    bot.send_message(cid, "Great! Glad your issue was resolved.\n\nHappy learning!")
    send_support_menu(bot, cid)
