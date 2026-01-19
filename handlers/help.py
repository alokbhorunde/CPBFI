from telebot import types
from handlers.menu import send_support_menu


def register(bot):
    """Register help command handler for groups and DMs."""
    
    @bot.message_handler(func=lambda m: m.text and (
        m.text.lower().strip() == "help" or 
        m.text.lower().startswith("/help") or
        " help " in f" {m.text.lower()} "
    ))
    def help_handler(message):
        chat_id = message.chat.id
        user_id = message.from_user.id

        if message.chat.type in ["group", "supergroup"]:
            try:
                # Send welcome message with menu directly to user's DM
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
                
                bot.send_message(
                    user_id,
                    "👋 **CPBFI Helpdesk**\nChoose a category below:",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
                
                # Create button to go to bot DM
                dm_markup = types.InlineKeyboardMarkup()
                dm_markup.add(types.InlineKeyboardButton(
                    "💬 Go to Chat", 
                    url=f"https://t.me/{bot.get_me().username}"
                ))
                bot.reply_to(message, "📩 I have messaged you, you can tell me your issue there", 
                           reply_markup=dm_markup)
            except:
                bot.reply_to(message, "⚠️ Please click 'Start' on my profile so I can DM you.")
        else:
            send_support_menu(bot, chat_id)
