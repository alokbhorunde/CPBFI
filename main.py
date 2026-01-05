import os
import telebot
from telebot import types
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ----------------------------------------------------------
# CONFIG KEYS (from .env)
# ----------------------------------------------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# FREE AI CLIENT (Groq)
groq_client = Groq(api_key=GROQ_API_KEY)


# ----------------------------------------------------------
# EMAIL FUNCTION (future use)
# ----------------------------------------------------------
def send_email_to_it(user, issue):
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    receiver_email = os.getenv("RECEIVER_EMAIL")

    smtp_server = "smtp.gmail.com"
    port = 587

    subject = f"CRITICAL ISSUE: {issue.upper()}"
    body = f"""
A critical issue was detected.

User: {user}
Issue Category: {issue}

Please check the problem immediately.
"""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
    except Exception as e:
        print("Email error:", e)


# ----------------------------------------------------------
# AI SYSTEM PROMPT (for troubleshooting)
# ----------------------------------------------------------
SYSTEM_PROMPT = """You are an IT Helpdesk Support Assistant for an online learning platform. Give SHORT, CONCISE responses - maximum 2-3 sentences.

RESPONSE RULES:
- Keep responses brief and to the point (2-3 sentences max)
- Give ONE clear solution at a time
- No long explanations or multiple steps
- Be friendly but direct
- If unclear, ask ONE clarifying question

COMMON ISSUES:
- Login: Check internet, try incognito, reset password
- Assessment: Refresh page, check time window
- LMS/Videos: Clear cache, try different browser
- Certificates: Complete course first, wait 24-48 hours
- Profile: Check file size (<2MB), use Chrome

End with: "Still stuck? Share a screenshot." (only if needed)"""


# ----------------------------------------------------------
# HUMAN-LIKE CHAT PROMPT (for Chat with AI Assistant)
# ----------------------------------------------------------
HUMAN_CHAT_PROMPT = """You are a friendly human support agent named "Support" for an online learning platform. Talk like a real person - warm, casual, and helpful.

YOUR PERSONALITY:
- Talk like a real human, not a robot
- Use casual language: "Hey!", "Got it!", "No worries!", "Let me help you with that"
- Show empathy: "I understand that's frustrating", "I'm sorry you're facing this"
- Be conversational and natural
- Use short sentences, like texting a friend
- Add friendly emojis occasionally 😊

RESPONSE STYLE:
- 2-4 short sentences max
- Sound like you're chatting, not reading from a script
- Ask follow-up questions naturally
- If you can help, help quickly
- If you can't, be honest

KNOWLEDGE:
- Login issues, password resets
- Assessment/test problems
- LMS navigation
- Certificate queries
- General platform help

Remember: You're a helpful friend, not a formal bot!"""


# ----------------------------------------------------------
# FREE AI MODEL FUNCTION
# ----------------------------------------------------------
def ask_ai_free(prompt, human_mode=False):
    try:
        system = HUMAN_CHAT_PROMPT if human_mode else SYSTEM_PROMPT
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI error:", e)
        return "AI system is unavailable right now."


# ----------------------------------------------------------
# STATES
# ----------------------------------------------------------
user_ai_mode = {}        # For "Other Issue"
user_ai_chat_mode = {}   # For "Chat with AI Assistant"


# ----------------------------------------------------------
# MAIN SUPPORT MENU
# ----------------------------------------------------------
def send_support_menu(chat_id):
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


# ----------------------------------------------------------
# "help" — Redirect group to DM
# ----------------------------------------------------------
@bot.message_handler(func=lambda m: m.text and "help" in m.text.lower())
def help_handler(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    if message.chat.type in ["group", "supergroup"]:
        try:
            # Send welcome message with menu directly
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
                "👋 Hi! I'm here to help you.\nChoose a category below:",
                reply_markup=markup
            )
            # Create button to go to bot DM
            dm_markup = types.InlineKeyboardMarkup()
            dm_markup.add(types.InlineKeyboardButton("💬 Go to Chat", url=f"https://t.me/{bot.get_me().username}"))
            bot.reply_to(message, "📩 I have messaged you, you can tell me your issue there", reply_markup=dm_markup)
        except:
            bot.reply_to(message, "⚠️ Please click 'Start' on my profile so I can DM you.")
    else:
        send_support_menu(chat_id)


# ----------------------------------------------------------
# CALLBACK HANDLER (ALL BUTTON WORK)
# ----------------------------------------------------------
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    cid = call.message.chat.id
    data = call.data

    # --------------------------------------------------
    # LOGIN
    # --------------------------------------------------
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

    # --------------------------------------------------
    # PCQ
    # --------------------------------------------------
    if data == "pcq":
        markup = types.InlineKeyboardMarkup()
        yes = types.InlineKeyboardButton("✔ Worked", callback_data="pcq_fixed")
        no = types.InlineKeyboardButton("➡ Next Step", callback_data="pcq_step2")
        markup.add(yes, no)

        bot.send_message(cid,
            "📝 **PCQ Help — Step 1**\n\n"
            "Please refresh the PCQ page once.\n\n"
            "Did it work?",
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif data == "pcq_step2":
        bot.send_message(cid,
            "📝 **PCQ Help — Step 2**\n"
            "Try opening PCQ in **Chrome or Edge**.\n\n"
            "Still facing issues? Describe the problem.",
            parse_mode="Markdown"
        )

    elif data == "pcq_fixed":
        bot.send_message(cid, "🎉 PCQ issue resolved!")

    # --------------------------------------------------
    # POST ASSESSMENT
    # --------------------------------------------------
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

    # --------------------------------------------------
    # LMS
    # --------------------------------------------------
    if data == "lms":
        bot.send_message(cid,
            "📘 **LMS Help**\n"
            "Try:\n• Refresh dashboard\n• Clear cache\n• Try another browser/device\n\n"
            "If still stuck, share details or screenshot.",
            parse_mode="Markdown"
        )

    # --------------------------------------------------
    # NAVIGATION HELP
    # --------------------------------------------------
    if data == "navhelp":
        bot.send_message(cid,
            "📱 **Navigation Help**\n\n"
            "I can guide you with:\n"
            "• Login\n• PCQ\n• Post Assessment\n• LMS Usage\n\n"
            "Tell me what you want help with.",
            parse_mode="Markdown"
        )

    # --------------------------------------------------
    # OTHER ISSUE → AI MODE (ONE MESSAGE)
    # --------------------------------------------------
    if data == "other":
        user_ai_mode[cid] = True
        bot.send_message(cid,
            "❓ Describe your issue.\n"
            "AI will analyze it and reply."
        )

    # --------------------------------------------------
    # AI CHAT MODE (FULL CHAT)
    # --------------------------------------------------
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

    if data == "exit_ai_chat":
        user_ai_chat_mode[cid] = False
        bot.send_message(cid, "You have exited AI Chat.")
        send_support_menu(cid)


# ----------------------------------------------------------
# MESSAGE HANDLER FOR: OTHER ISSUE → ONE AI RESPONSE
# ----------------------------------------------------------
@bot.message_handler(func=lambda msg: user_ai_mode.get(msg.chat.id) is True)
def ai_issue_handler(message):
    cid = message.chat.id
    query = message.text

    bot.send_chat_action(cid, "typing")
    ai_reply = ask_ai_free(query)

    bot.send_message(cid, ai_reply)
    user_ai_mode[cid] = False  # disable after 1 use


# ----------------------------------------------------------
# MESSAGE HANDLER FOR: FULL AI CHAT MODE
# ----------------------------------------------------------
@bot.message_handler(func=lambda msg: user_ai_chat_mode.get(msg.chat.id) is True)
def ai_chat_handler(message):
    cid = message.chat.id
    user_msg = message.text

    bot.send_chat_action(cid, "typing")
    ai_response = ask_ai_free(user_msg, human_mode=True)

    bot.send_message(cid, ai_response)


# ----------------------------------------------------------
# CATCH-ALL HANDLER FOR: User describes issue (DM only)
# ----------------------------------------------------------
@bot.message_handler(func=lambda msg: msg.chat.type == "private")
def general_message_handler(message):
    cid = message.chat.id
    user_msg = message.text

    # Respond with AI for any message in DM
    bot.send_chat_action(cid, "typing")
    ai_response = ask_ai_free(user_msg)
    bot.send_message(cid, ai_response)


# ----------------------------------------------------------
# RUN BOT
# ----------------------------------------------------------
if __name__ == "__main__":
    print("🤖 Bot is running...")
    bot.infinity_polling()
