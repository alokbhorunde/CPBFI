from telebot import types
from datetime import datetime, timedelta


# State for PCQ timing feature
user_pcq_timing = {}


def register(bot):
    """Register all PCQ-related callback and message handlers."""
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("pcq"))
    def handle_pcq(call):
        cid = call.message.chat.id
        data = call.data

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


def check_pcq_timing_keywords(message_text):
    """Check if message contains PCQ 30-min timing keywords."""
    keywords = ["30 min", "30min", "revised time", "can't start quiz", 
                "cant start quiz", "quiz not accessible", "30 minute"]
    return any(keyword in message_text.lower() for keyword in keywords)


def start_timing_flow(bot, cid):
    """Start the PCQ timing check flow."""
    user_pcq_timing[cid] = True
    bot.send_message(cid, 
        "🕐 I see you're facing the **30-minute timing issue** with PCQ.\n\n"
        "Let me help you check if you can access the quiz now.\n\n"
        "📝 **What was your scheduled quiz time?**\n"
        "(Example: 10:30 or 2:00 PM)",
        parse_mode="Markdown"
    )


def handle_timing_response(bot, message):
    """Handle user's time input for PCQ timing calculation."""
    cid = message.chat.id
    user_input = message.text.strip()
    
    bot.send_chat_action(cid, "typing")
    
    try:
        # Try different time formats
        scheduled_time = None
        for fmt in ["%H:%M", "%I:%M %p", "%I:%M%p", "%H.%M", "%I.%M %p"]:
            try:
                scheduled_time = datetime.strptime(user_input.upper(), fmt)
                break
            except:
                continue
        
        if not scheduled_time:
            bot.send_message(cid, 
                "❌ Sorry, I couldn't understand that time format.\n\n"
                "Please enter your scheduled time like:\n"
                "• 10:30\n• 2:00 PM\n• 14:30")
            return
        
        # Get current time (IST)
        now = datetime.now()
        scheduled_today = now.replace(hour=scheduled_time.hour, minute=scheduled_time.minute, second=0)
        
        # Quiz is accessible ONLY within 30 min of scheduled time
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


def is_in_timing_mode(chat_id):
    """Check if user is in PCQ timing mode."""
    return user_pcq_timing.get(chat_id, False)
