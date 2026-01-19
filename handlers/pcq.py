from telebot import types
from datetime import datetime, timedelta
from handlers.menu import send_support_menu
from utils.ai import ask_ai_free
from utils.email import send_email_to_it

# State for PCQ timing input
user_pcq_timing = {}

# State for "Other PCQ Issue" - free text input
user_pcq_other_mode = {}

# Track escalation attempts per user
user_pcq_escalation_attempts = {}

# Track user details collection for PCQ escalation
user_pcq_detail_collection = {}


def register(bot):
    """Register all PCQ-related callback handlers."""
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("pcq"))
    def handle_pcq(call):
        cid = call.message.chat.id
        data = call.data

        # --------------------------------------------------
        # STEP 1: Identify PCQ Problem (Entry Point)
        # --------------------------------------------------
        if data == "pcq":
            # Reset attempts
            user_pcq_escalation_attempts[cid] = {"count": 0, "issue": ""}
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("📍 Where is the Quiz?", callback_data="pcq_where"),
                types.InlineKeyboardButton("🧪 Test Not Showing", callback_data="pcq_not_showing"),
                types.InlineKeyboardButton("🔄 Unable to Submit", callback_data="pcq_submit"),
                types.InlineKeyboardButton("🚪 Exited Midway", callback_data="pcq_exited"),
                types.InlineKeyboardButton("⏰ Joined Late / PCQ Time Issue", callback_data="pcq_time"),
                types.InlineKeyboardButton("❓ Other PCQ Issue", callback_data="pcq_other"),
                types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="pcq_back_menu")
            )

            bot.send_message(cid,
                "📝 **PCQ Issue — Skillserv Portal**\n\n"
                "What PCQ-related issue are you facing?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # --------------------------------------------------
        # FLOW A: Where is the Quiz?
        # --------------------------------------------------
        elif data == "pcq_where":
            track_pcq_issue(cid, "Where is the Quiz")
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🔄 Refresh & Try Again", callback_data="pcq_where_refresh"),
                types.InlineKeyboardButton("❓ Still Not Visible", callback_data="pcq_still_not_working"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="pcq")
            )

            bot.send_message(cid,
                "📍 **Where is the Quiz?**\n\n"
                "To access the PCQ quiz on Skillserv:\n\n"
                "1️⃣ Login to the Skillserv portal.\n"
                "2️⃣ Go to your dashboard.\n"
                "3️⃣ Look for the PCQ / Assessment section.\n"
                "4️⃣ Click on the active quiz link.\n\n"
                "If you still cannot find it, please try refreshing the page once.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "pcq_where_refresh":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("✅ Found it!", callback_data="pcq_fixed"),
                types.InlineKeyboardButton("❓ Still Not Visible", callback_data="pcq_still_not_working"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="pcq_where")
            )

            bot.send_message(cid,
                "🔄 **Refresh & Try Again**\n\n"
                "1️⃣ Press Ctrl+F5 to hard refresh\n"
                "2️⃣ Or close and reopen the browser\n"
                "3️⃣ Login again and check the dashboard\n\n"
                "Can you see the quiz now?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # --------------------------------------------------
        # FLOW B: Test Not Showing
        # --------------------------------------------------
        elif data == "pcq_not_showing":
            track_pcq_issue(cid, "Test Not Showing")
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🔄 Tried All Steps", callback_data="pcq_still_not_working"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="pcq")
            )

            bot.send_message(cid,
                "🧪 **Test Not Showing**\n\n"
                "If the PCQ test is not showing, please try the following:\n\n"
                "1️⃣ Refresh the page once.\n"
                "2️⃣ Ensure you are logged in using the registered email ID.\n"
                "3️⃣ Close the browser tab and login again.\n"
                "4️⃣ Try accessing the portal from another device or browser.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # --------------------------------------------------
        # FLOW C: Unable to Submit
        # --------------------------------------------------
        elif data == "pcq_submit":
            track_pcq_issue(cid, "Unable to Submit")
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🚪 Had to Exit Midway", callback_data="pcq_exited"),
                types.InlineKeyboardButton("❓ Still Unable to Submit", callback_data="pcq_still_not_working"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="pcq")
            )

            bot.send_message(cid,
                "🔄 **Unable to Submit**\n\n"
                "If you are unable to submit the PCQ:\n\n"
                "1️⃣ Ensure all questions are attempted.\n"
                "2️⃣ Check your internet connection.\n"
                "3️⃣ Wait for a few seconds and try submitting again.\n"
                "4️⃣ Avoid refreshing the page repeatedly.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # --------------------------------------------------
        # FLOW D: Exited Midway
        # --------------------------------------------------
        elif data == "pcq_exited":
            track_pcq_issue(cid, "Exited Midway")
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🔄 Tried Rejoining", callback_data="pcq_rejoin_tried"),
                types.InlineKeyboardButton("❓ Cannot Rejoin", callback_data="pcq_still_not_working"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="pcq")
            )

            bot.send_message(cid,
                "🚪 **Exited Midway**\n\n"
                "If you exited the PCQ midway:\n\n"
                "• In most cases, re-entry depends on system rules.\n"
                "• Please login again and check if the quiz resumes automatically.\n\n"
                "If the test does not resume, you may need support assistance.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "pcq_rejoin_tried":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("✅ Resumed Successfully", callback_data="pcq_fixed"),
                types.InlineKeyboardButton("❓ Cannot Rejoin", callback_data="pcq_still_not_working"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="pcq_exited")
            )

            bot.send_message(cid,
                "🔄 **Tried Rejoining**\n\n"
                "Were you able to resume the quiz?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # --------------------------------------------------
        # FLOW E: Joined Late / PCQ Time Issue
        # --------------------------------------------------
        elif data == "pcq_time":
            track_pcq_issue(cid, "Joined Late / Time Issue")
            user_pcq_timing[cid] = True
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="pcq"))

            bot.send_message(cid,
                "⏰ **Joined Late / PCQ Time Issue**\n\n"
                "Please enter the scheduled PCQ start time (HH:MM format).\n\n"
                "Example: `10:00` or `2:30 PM`",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # PCQ Time - Joining Now
        elif data == "pcq_time_joining":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("✅ Joined Successfully", callback_data="pcq_fixed"),
                types.InlineKeyboardButton("❓ Facing Issue", callback_data="pcq_still_not_working"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="pcq_time")
            )

            bot.send_message(cid,
                "🚀 **Great! Join immediately!**\n\n"
                "If you face any issue while joining, let me know.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # --------------------------------------------------
        # FLOW F: Other PCQ Issue
        # --------------------------------------------------
        elif data == "pcq_other":
            user_pcq_other_mode[cid] = True
            track_pcq_issue(cid, "Other PCQ Issue")
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="pcq"))

            bot.send_message(cid,
                "❓ **Other PCQ Issue**\n\n"
                "Please briefly describe the PCQ issue you are facing.\n"
                "Our AI will analyze and provide help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # --------------------------------------------------
        # STILL NOT WORKING - Track attempts (2-3 times)
        # --------------------------------------------------
        elif data == "pcq_still_not_working":
            # Increment attempt counter
            if cid not in user_pcq_escalation_attempts:
                user_pcq_escalation_attempts[cid] = {"count": 1, "issue": "PCQ Issue"}
            else:
                user_pcq_escalation_attempts[cid]["count"] += 1
            
            attempts = user_pcq_escalation_attempts[cid]["count"]
            
            if attempts >= 2:
                # After 2+ attempts, start collecting user details
                start_pcq_detail_collection(bot, cid, user_pcq_escalation_attempts[cid].get("issue", "PCQ Issue"))
            else:
                # First attempt - give another chance
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton("🔁 Try Again", callback_data="pcq"),
                    types.InlineKeyboardButton("❓ Still Not Working", callback_data="pcq_still_not_working"),
                    types.InlineKeyboardButton("⬅️ Back", callback_data="pcq")
                )

                bot.send_message(cid,
                    "⚠️ **Let's try once more**\n\n"
                    "Please try the following:\n"
                    "1️⃣ Clear your browser cache\n"
                    "2️⃣ Try in Incognito/Private mode\n"
                    "3️⃣ Use a different browser or device\n\n"
                    f"_Attempt {attempts}/2 - After 2 attempts, we'll connect you with support._",
                    parse_mode="Markdown",
                    reply_markup=markup
                )

        # --------------------------------------------------
        # Fixed / Success
        # --------------------------------------------------
        elif data == "pcq_fixed":
            # Reset attempts
            if cid in user_pcq_escalation_attempts:
                user_pcq_escalation_attempts[cid] = {"count": 0, "issue": ""}
            
            bot.send_message(cid, "🎉 Great! Your PCQ issue is resolved.\n\nBest of luck with your assessment! 📚")
            send_support_menu(bot, cid)

        # --------------------------------------------------
        # Back to Main Menu
        # --------------------------------------------------
        elif data == "pcq_back_menu":
            send_support_menu(bot, cid)


def track_pcq_issue(cid, issue):
    """Track the current issue type for a user."""
    if cid not in user_pcq_escalation_attempts:
        user_pcq_escalation_attempts[cid] = {"count": 0, "issue": issue}
    else:
        user_pcq_escalation_attempts[cid]["issue"] = issue


def start_pcq_detail_collection(bot, cid, issue):
    """Start collecting user details for PCQ escalation."""
    user_pcq_detail_collection[cid] = {
        "step": "name",
        "name": "",
        "email": "",
        "bfsi": "",
        "issue": issue
    }
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="pcq"))
    
    bot.send_message(cid,
        "📝 **Escalating to Support Team**\n\n"
        "We need a few details to help you faster.\n\n"
        "**Step 1/3:** Please enter your **Full Name**:",
        parse_mode="Markdown",
        reply_markup=markup
    )


def is_in_pcq_detail_collection_mode(chat_id):
    """Check if user is in PCQ detail collection mode."""
    return chat_id in user_pcq_detail_collection and user_pcq_detail_collection[chat_id].get("step") is not None


def handle_pcq_detail_collection(bot, message):
    """Handle user input during PCQ detail collection."""
    cid = message.chat.id
    user_input = message.text.strip()
    
    if cid not in user_pcq_detail_collection:
        return False
    
    current_step = user_pcq_detail_collection[cid]["step"]
    
    if current_step == "name":
        user_pcq_detail_collection[cid]["name"] = user_input
        user_pcq_detail_collection[cid]["step"] = "email"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="pcq"))
        
        bot.send_message(cid,
            f"✅ Name: **{user_input}**\n\n"
            "**Step 2/3:** Please enter your **Email ID**:",
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    elif current_step == "email":
        user_pcq_detail_collection[cid]["email"] = user_input
        user_pcq_detail_collection[cid]["step"] = "bfsi"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="pcq"))
        
        bot.send_message(cid,
            f"✅ Email: **{user_input}**\n\n"
            "**Step 3/3:** Please enter your **BFSI ID**:",
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    elif current_step == "bfsi":
        user_pcq_detail_collection[cid]["bfsi"] = user_input
        user_pcq_detail_collection[cid]["step"] = None  # Done collecting
        
        # Collect all details
        details = user_pcq_detail_collection[cid]
        
        # Send email to IT
        send_pcq_escalation_email(
            name=details["name"],
            email=details["email"],
            bfsi_id=details["bfsi"],
            issue=details["issue"],
            username=message.from_user.username or "N/A",
            user_id=message.from_user.id
        )
        
        # Confirm to user
        bot.send_message(cid,
            "✅ **PCQ Issue Escalated Successfully!**\n\n"
            f"📋 **Details Submitted:**\n"
            f"• Name: {details['name']}\n"
            f"• Email: {details['email']}\n"
            f"• BFSI ID: {details['bfsi']}\n"
            f"• Portal: Skillserv\n"
            f"• Issue: {details['issue']}\n\n"
            "🔔 Our support team will contact you shortly.\n"
            "📧 For urgent queries: support@cpbfi.org\n\n"
            "Thank you for your patience! 🙏",
            parse_mode="Markdown"
        )
        
        # Reset states
        if cid in user_pcq_escalation_attempts:
            user_pcq_escalation_attempts[cid] = {"count": 0, "issue": ""}
        del user_pcq_detail_collection[cid]
        
        send_support_menu(bot, cid)
    
    return True


def send_pcq_escalation_email(name, email, bfsi_id, issue, username, user_id):
    """Send PCQ escalation email to IT team."""
    try:
        send_email_to_it(f"{name} ({email})", f"PCQ - {issue} - Skillserv")
        print(f"📧 PCQ Escalation email sent for {name} ({email})")
    except Exception as e:
        print(f"❌ Email error: {e}")


def is_in_timing_mode(chat_id):
    """Check if user is in PCQ timing mode."""
    return user_pcq_timing.get(chat_id, False)


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
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="pcq")
            )
            
            bot.send_message(cid, 
                f"⏳ **Your quiz hasn't started yet!**\n\n"
                f"📅 Scheduled time: {scheduled_today.strftime('%I:%M %p')}\n"
                f"⏰ Current time: {now.strftime('%I:%M %p')}\n\n"
                f"⏱️ Wait **{int(wait_mins)} more minutes** until your scheduled time.",
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        elif now <= cutoff_time:
            # Within the 30-min window - should be accessible
            mins_left = (cutoff_time - now).total_seconds() / 60
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🚀 Joining Now", callback_data="pcq_time_joining"),
                types.InlineKeyboardButton("❓ Facing Issue", callback_data="pcq_still_not_working"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="pcq")
            )
            
            bot.send_message(cid, 
                f"⏳ **You are still within the allowed joining window!**\n\n"
                f"📅 Scheduled time: {scheduled_today.strftime('%I:%M %p')}\n"
                f"🚫 Cutoff time: {cutoff_time.strftime('%I:%M %p')}\n"
                f"⏰ Current time: {now.strftime('%I:%M %p')}\n\n"
                f"⏱️ You have **{int(mins_left)} minutes left** to join.\n\n"
                "⚠️ **Join ASAP!** Do not delay further.\n\n"
                "If you face any issue while joining, let me know.",
                parse_mode="Markdown",
                reply_markup=markup
            )
            
        else:
            # After 30 min - too late
            mins_late = (now - cutoff_time).total_seconds() / 60
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("❓ Talk to Support", callback_data="pcq_still_not_working"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="pcq")
            )
            
            bot.send_message(cid, 
                f"❌ **The allowed joining time has passed.**\n\n"
                f"📅 Scheduled time: {scheduled_today.strftime('%I:%M %p')}\n"
                f"🚫 Cutoff was: {cutoff_time.strftime('%I:%M %p')}\n"
                f"⏰ Current time: {now.strftime('%I:%M %p')}\n\n"
                f"You're **{int(mins_late)} minutes late**.\n\n"
                "PCQ entry is usually closed 30 minutes after the start time.\n"
                "You may need to contact support for further assistance.",
                parse_mode="Markdown",
                reply_markup=markup
            )
        
        user_pcq_timing[cid] = False
        
    except Exception as e:
        bot.send_message(cid, "❌ Couldn't process that. Please enter time like: 10:30 or 2:00 PM")
        print(f"PCQ timing error: {e}")


def check_pcq_timing_keywords(message_text):
    """Check if message contains PCQ 30-min timing keywords."""
    keywords = ["30 min", "30min", "revised time", "can't start quiz", 
                "cant start quiz", "quiz not accessible", "30 minute", "joined late"]
    return any(keyword in message_text.lower() for keyword in keywords)


def start_timing_flow(bot, cid):
    """Start the PCQ timing check flow."""
    user_pcq_timing[cid] = True
    bot.send_message(cid, 
        "🕐 **PCQ Time Check**\n\n"
        "Let me help you check if you can access the quiz now.\n\n"
        "📝 **What was your scheduled quiz time?**\n"
        "(Example: 10:30 or 2:00 PM)",
        parse_mode="Markdown"
    )


def is_in_pcq_other_mode(chat_id):
    """Check if user is in 'Other PCQ Issue' mode."""
    return user_pcq_other_mode.get(chat_id, False)


def handle_pcq_other_message(bot, message):
    """Handle free-text input for 'Other PCQ Issue'."""
    cid = message.chat.id
    user_query = message.text

    bot.send_chat_action(cid, "typing")
    
    # Use AI to respond to PCQ issue
    prompt = f"User is facing a PCQ issue on Skillserv portal. Their issue: {user_query}"
    ai_response = ask_ai_free(prompt)
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("✅ Issue Resolved", callback_data="pcq_fixed"),
        types.InlineKeyboardButton("❓ Still Need Help", callback_data="pcq_still_not_working"),
        types.InlineKeyboardButton("⬅️ Back to PCQ Menu", callback_data="pcq")
    )
    
    bot.send_message(cid, ai_response, reply_markup=markup)
    
    # Clear the mode
    user_pcq_other_mode[cid] = False
