import os
import telebot
from telebot import types
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime, timedelta

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
SYSTEM_PROMPT = """You are an IT Helpdesk Support Assistant for the CPBFI online learning platform.

GOAL:
Provide calm, reassuring, and SHORT responses that resolve student issues quickly.

RESPONSE RULES (STRICT):

- Maximum 2–3 sentences only
- ONE clear solution at a time
- No step-by-step lists
- No technical jargon
- Acknowledge the issue briefly
- If required, escalate politely
- Ask ONLY ONE clarifying question if needed
- End with: "Still stuck? Share a screenshot." (only when the issue may persist)

TONE:

- Polite, supportive, and professional
- Reduce anxiety, build confidence
- Never blame the user

SUPPORTED ISSUE CATEGORIES & STANDARD ACTIONS:

LOGIN (L1):

- Use shared credentials
- Use “Forgot Password” with registered email
- Recheck email, mobile number, and password carefully

TECHNICAL (L1):

- Refresh the page once
- Open the platform in Google Chrome
- Ensure stable internet connection

ASSESSMENT (L1):

- Refresh the test page (answers stay safe)
- Open the test in Chrome on a stable network
- If submission fails, escalate to IT team

PROFILE / REGISTRATION (L1):

- Ensure document format and size are correct
- If form issue persists, inform it’s under review

COURSE ACCESS & CONTENT (L2):

- Check Dashboard → Recorded Videos
- Refresh or reopen in Chrome

NAVIGATION (L3):

- Guide to Dashboard → Course Section

CERTIFICATES (L2):

- Certificates are generated as per announced schedule
- Ask user to wait for notification if timeline not passed

MISCELLANEOUS (L3):

- Attendance issues → contact student coordinator
- Out-of-scope → ask for a clear platform-related issue

DO NOT:

- Give multiple fixes together
- Over-explain
- Mention internal priorities (L1/L2/L3) to users"""


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
user_pcq_timing = {}     # For PCQ 30-min timing issue


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
                "👋 **CPBFI Helpdesk**\nChoose a category below:",
                reply_markup=markup,
                parse_mode="Markdown"
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
# MESSAGE HANDLER FOR: PCQ TIMING ISSUE
# ----------------------------------------------------------
@bot.message_handler(func=lambda msg: user_pcq_timing.get(msg.chat.id) is True)
def pcq_timing_handler(message):
    cid = message.chat.id
    user_input = message.text.strip()
    
    bot.send_chat_action(cid, "typing")
    
    # Try to parse the time
    try:
        # Try different formats
        scheduled_time = None
        for fmt in ["%H:%M", "%I:%M %p", "%I:%M%p", "%H.%M", "%I.%M %p"]:
            try:
                scheduled_time = datetime.strptime(user_input.upper(), fmt)
                break
            except:
                continue
        
        if not scheduled_time:
            bot.send_message(cid, "❌ Sorry, I couldn't understand that time format.\n\nPlease enter your scheduled time like:\n• 10:30\n• 2:00 PM\n• 14:30")
            return
        
        # Get current time (IST)
        now = datetime.now()
        scheduled_today = now.replace(hour=scheduled_time.hour, minute=scheduled_time.minute, second=0)
        
        # Quiz is accessible ONLY within 30 min of scheduled time
        # After scheduled + 30 min = quiz becomes INACCESSIBLE
        cutoff_time = scheduled_today + timedelta(minutes=30)
        
        if now < scheduled_today:
            # Before scheduled time
            wait_mins = (scheduled_today - now).total_seconds() / 60
            bot.send_message(cid, 
                f"⏳ Your quiz hasn't started yet!\n\n"
                f"📅 Scheduled time: {scheduled_today.strftime('%I:%M %p')}\n"
                f"⏰ Current time: {now.strftime('%I:%M %p')}\n\n"
                f"⏱️ Wait {int(wait_mins)} more minutes until your scheduled time.")
        elif now <= cutoff_time:
            # Within the 30-min window - should be accessible
            mins_left = (cutoff_time - now).total_seconds() / 60
            bot.send_message(cid, 
                f"✅ You should be able to access the quiz now!\n\n"
                f"📅 Scheduled time: {scheduled_today.strftime('%I:%M %p')}\n"
                f"🚫 Cutoff time: {cutoff_time.strftime('%I:%M %p')}\n"
                f"⏰ Current time: {now.strftime('%I:%M %p')}\n\n"
                f"You have {int(mins_left)} minutes left to start.\n\n"
                f"Try refreshing the page. If still not working, clear cache and try in incognito mode.")
        else:
            # After 30 min - too late
            mins_late = (now - cutoff_time).total_seconds() / 60
            bot.send_message(cid, 
                f"❌ Your quiz window has expired.\n\n"
                f"📅 Scheduled time: {scheduled_today.strftime('%I:%M %p')}\n"
                f"🚫 Cutoff was: {cutoff_time.strftime('%I:%M %p')}\n"
                f"⏰ Current time: {now.strftime('%I:%M %p')}\n\n"
                f"You're {int(mins_late)} minutes late. The quiz is no longer accessible.")
        
        user_pcq_timing[cid] = False
        
    except Exception as e:
        bot.send_message(cid, "❌ Couldn't process that. Please enter time like: 10:30 or 2:00 PM")
        print(f"PCQ timing error: {e}")


# ----------------------------------------------------------
# CATCH-ALL HANDLER FOR: User describes issue (DM only)
# ----------------------------------------------------------
@bot.message_handler(func=lambda msg: msg.chat.type == "private")
def general_message_handler(message):
    cid = message.chat.id
    user_msg = message.text.lower() if message.text else ""
    
    bot.send_chat_action(cid, "typing")
    
    # Check for PCQ 30-min timing issue
    if any(keyword in user_msg for keyword in ["30 min", "30min", "revised time", "can't start quiz", "cant start quiz", "quiz not accessible", "30 minute"]):
        user_pcq_timing[cid] = True
        bot.send_message(cid, 
            "🕐 I see you're facing the **30-minute timing issue** with PCQ.\n\n"
            "Let me help you check if you can access the quiz now.\n\n"
            "📝 **What was your scheduled quiz time?**\n"
            "(Example: 10:30 or 2:00 PM)",
            parse_mode="Markdown"
        )
        return
    
    # Respond with AI for any other message
    ai_response = ask_ai_free(message.text)
    bot.send_message(cid, ai_response)


# ----------------------------------------------------------
# PHOTO HANDLER: Respond to screenshots
# ----------------------------------------------------------
@bot.message_handler(content_types=['photo'])
def photo_handler(message):
    cid = message.chat.id
    caption = message.caption if message.caption else ""
    
    bot.send_chat_action(cid, "typing")
    
    # Acknowledge the screenshot and provide help
    response = f"📸 Thanks for sharing the screenshot! I can see you're facing an issue.\n\n"
    
    if "pcq" in caption.lower() or "quiz" in caption.lower():
        response += "This looks like a PCQ/Quiz access issue. The error usually means:\n• You're outside the allowed time window\n• Wait 30 minutes after the revised time and try again\n\nStill stuck? Describe the exact issue and I'll help!"
    elif "login" in caption.lower() or "password" in caption.lower():
        response += "I see this is a login issue. Try:\n• Clear browser cache\n• Use incognito mode\n• Reset password if needed\n\nStill stuck? Let me know more details!"
    else:
        response += "Please describe what issue you're facing in this screenshot, and I'll help you fix it! 😊"
    
    bot.send_message(cid, response)


# ----------------------------------------------------------
# RUN BOT
# ----------------------------------------------------------
if __name__ == "__main__":
    print("🤖 Bot is running...")
    bot.infinity_polling()
