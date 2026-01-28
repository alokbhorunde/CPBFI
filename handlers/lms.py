from telebot import types
from handlers.menu import send_support_menu
from utils.ai import ask_ai_free
from utils.email import send_email_to_it

# State for "Other LMS Issue" - free text input
user_lms_other_mode = {}

# Track escalation attempts per user
user_lms_escalation_attempts = {}

# Track user details collection for LMS escalation
user_lms_detail_collection = {}


def register(bot):
    """Register all LMS-related callback handlers."""
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("lms"))
    def handle_lms(call):
        cid = call.message.chat.id
        data = call.data

        # ==================================================
        # STEP 1: LMS Issue Selection (Main LMS Menu)
        # ==================================================
        if data == "lms":
            # Reset attempts
            user_lms_escalation_attempts[cid] = {"count": 0, "issue": ""}
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🎬 Batch Videos Not Visible", callback_data="lms_videos_not_visible"),
                types.InlineKeyboardButton("▶️ Videos Not Playing", callback_data="lms_videos_not_playing"),
                types.InlineKeyboardButton("📊 Progress / Completion Not Updated", callback_data="lms_progress"),
                types.InlineKeyboardButton("⏳ Course Expired / Access Duration", callback_data="lms_expired"),
                types.InlineKeyboardButton("❓ Other LMS Issue", callback_data="lms_other"),
                types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="lms_back_menu")
            )

            bot.send_message(cid,
                "📖 **LMS / Videos Issue**\n\n"
                "Please select the LMS-related issue you are facing 👇",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # ==================================================
        # FLOW A — 🎬 Batch Videos Not Visible
        # ==================================================
        elif data == "lms_videos_not_visible":
            track_lms_issue(cid, "Batch Videos Not Visible")
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🔄 I'll Check Again", callback_data="lms_fixed"),
                types.InlineKeyboardButton("❓ Still Not Visible", callback_data="lms_still_not_working"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="lms")
            )

            bot.send_message(cid,
                "🎬 **Batch Videos Not Visible**\n\n"
                "If batch launch videos are not visible on your dashboard, please note:\n\n"
                "1️⃣ Batch videos are assigned only after batch launch.\n"
                "2️⃣ System sync may take some time after launch.\n"
                "3️⃣ Log out and log in again.\n"
                "4️⃣ Refresh your dashboard and check for updates.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # ==================================================
        # FLOW B — ▶️ Videos Not Playing
        # ==================================================
        elif data == "lms_videos_not_playing":
            track_lms_issue(cid, "Videos Not Playing")
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🔄 Tried All Steps", callback_data="lms_still_not_working"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="lms")
            )

            bot.send_message(cid,
                "▶️ **Videos Not Playing**\n\n"
                "If videos are not playing on the LMS, try the following steps:\n\n"
                "1️⃣ Use Google Chrome browser (recommended).\n"
                "2️⃣ Check your internet connection.\n"
                "3️⃣ Refresh the page once.\n"
                "4️⃣ Clear browser cache if required.\n"
                "5️⃣ Log out and log in again before retrying.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # ==================================================
        # FLOW C — 📊 Progress / Completion Not Updated
        # ==================================================
        elif data == "lms_progress":
            track_lms_issue(cid, "Progress / Completion Not Updated")
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🔄 I'll Recheck Progress", callback_data="lms_fixed"),
                types.InlineKeyboardButton("❓ Still Not Updated", callback_data="lms_still_not_working"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="lms")
            )

            bot.send_message(cid,
                "📊 **Progress / Completion Not Updated**\n\n"
                "If your learning progress or completion status is not updating:\n\n"
                "1️⃣ LMS progress may take time to sync with the portal.\n"
                "2️⃣ Ensure all required videos/modules are completed.\n"
                "3️⃣ Follow the learning sequence strictly.\n"
                "4️⃣ Avoid skipping videos.\n"
                "5️⃣ Log out and log in again after some time.\n"
                "6️⃣ Refresh the dashboard.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # ==================================================
        # FLOW D — ⏳ Course Expired / LMS Access Duration
        # ==================================================
        elif data == "lms_expired":
            track_lms_issue(cid, "Course Expired / Access Duration")
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("⬅️ Back to LMS Menu", callback_data="lms"),
                types.InlineKeyboardButton("❓ Still Have a Question", callback_data="lms_still_not_working")
            )

            bot.send_message(cid,
                "⏳ **Course Expired / LMS Access Duration**\n\n"
                "Regarding LMS content access:\n\n"
                "📅 LMS access is available for:\n"
                "➡️ **30 to 45 days** from the batch launch date.\n\n"
                "After this period, course content may show as expired.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # ==================================================
        # FLOW E — ❓ Other LMS Issue
        # ==================================================
        elif data == "lms_other":
            user_lms_other_mode[cid] = True
            track_lms_issue(cid, "Other LMS Issue")
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="lms"))

            bot.send_message(cid,
                "❓ **Other LMS Issue**\n\n"
                "Please briefly describe the LMS issue you are facing.\n"
                "Our support team will review it.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # ==================================================
        # STILL NOT WORKING - Track attempts (2 times)
        # ==================================================
        elif data == "lms_still_not_working":
            # Increment attempt counter
            if cid not in user_lms_escalation_attempts:
                user_lms_escalation_attempts[cid] = {"count": 1, "issue": "LMS Issue"}
            else:
                user_lms_escalation_attempts[cid]["count"] += 1
            
            attempts = user_lms_escalation_attempts[cid]["count"]
            
            if attempts >= 2:
                # After 2+ attempts, start collecting user details for escalation
                start_lms_detail_collection(bot, cid, user_lms_escalation_attempts[cid].get("issue", "LMS Issue"))
            else:
                # First attempt - give another chance
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton("🔁 Try Again", callback_data="lms"),
                    types.InlineKeyboardButton("❓ Still Not Working", callback_data="lms_still_not_working"),
                    types.InlineKeyboardButton("⬅️ Back", callback_data="lms")
                )

                bot.send_message(cid,
                    "⚠️ **Let's try once more**\n\n"
                    "Please try the following:\n"
                    "1️⃣ Clear your browser cache\n"
                    "2️⃣ Try in Incognito/Private mode\n"
                    "3️⃣ Use a different browser (Chrome recommended)\n"
                    "4️⃣ Check your internet connection\n\n"
                    f"_Attempt {attempts}/2 - After 2 attempts, we'll connect you with support._",
                    parse_mode="Markdown",
                    reply_markup=markup
                )

        # ==================================================
        # Fixed / Success
        # ==================================================
        elif data == "lms_fixed":
            # Reset attempts
            if cid in user_lms_escalation_attempts:
                user_lms_escalation_attempts[cid] = {"count": 0, "issue": ""}
            
            bot.send_message(cid, "🎉 Great! Your LMS issue is resolved.\n\nHappy Learning! 📚")
            send_support_menu(bot, cid)

        # ==================================================
        # Back to Main Menu
        # ==================================================
        elif data == "lms_back_menu":
            send_support_menu(bot, cid)


def track_lms_issue(cid, issue):
    """Track the current issue type for a user."""
    if cid not in user_lms_escalation_attempts:
        user_lms_escalation_attempts[cid] = {"count": 0, "issue": issue}
    else:
        user_lms_escalation_attempts[cid]["issue"] = issue


def start_lms_detail_collection(bot, cid, issue):
    """Start collecting user details for LMS escalation."""
    user_lms_detail_collection[cid] = {
        "step": "name",
        "name": "",
        "email": "",
        "bfsi": "",
        "issue": issue
    }
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="lms"))
    
    bot.send_message(cid,
        "📝 **Escalating LMS Issue to Support Team**\n\n"
        "We need a few details to help you faster.\n\n"
        "**Step 1/3:** Please enter your **Full Name**:",
        parse_mode="Markdown",
        reply_markup=markup
    )


def is_in_lms_detail_collection_mode(chat_id):
    """Check if user is in LMS detail collection mode."""
    return chat_id in user_lms_detail_collection and user_lms_detail_collection[chat_id].get("step") is not None


def handle_lms_detail_collection(bot, message):
    """Handle user input during LMS detail collection."""
    cid = message.chat.id
    user_input = message.text.strip()
    
    if cid not in user_lms_detail_collection:
        return False
    
    current_step = user_lms_detail_collection[cid]["step"]
    
    if current_step == "name":
        user_lms_detail_collection[cid]["name"] = user_input
        user_lms_detail_collection[cid]["step"] = "email"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="lms"))
        
        bot.send_message(cid,
            f"✅ Name: **{user_input}**\n\n"
            "**Step 2/3:** Please enter your **Email ID**:",
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    elif current_step == "email":
        user_lms_detail_collection[cid]["email"] = user_input
        user_lms_detail_collection[cid]["step"] = "bfsi"
        
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="lms"))
        
        bot.send_message(cid,
            f"✅ Email: **{user_input}**\n\n"
            "**Step 3/3:** Please enter your **BFSI ID**:",
            parse_mode="Markdown",
            reply_markup=markup
        )
    
    elif current_step == "bfsi":
        user_lms_detail_collection[cid]["bfsi"] = user_input
        user_lms_detail_collection[cid]["step"] = None  # Done collecting
        
        # Collect all details
        details = user_lms_detail_collection[cid]
        
        # Send email to IT
        send_lms_escalation_email(
            name=details["name"],
            email=details["email"],
            bfsi_id=details["bfsi"],
            issue=details["issue"],
            username=message.from_user.username or "N/A",
            user_id=message.from_user.id
        )
        
        # Confirm to user
        bot.send_message(cid,
            "✅ **LMS Issue Escalated Successfully!**\n\n"
            f"📋 **Details Submitted:**\n"
            f"• Name: {details['name']}\n"
            f"• Email: {details['email']}\n"
            f"• BFSI ID: {details['bfsi']}\n"
            f"• Issue Type: LMS / Videos\n"
            f"• Issue: {details['issue']}\n\n"
            "🔔 Our support team will contact you shortly.\n"
            "📧 For urgent queries: support@cpbfi.org\n\n"
            "Please allow some time for review. Thank you! 🙏",
            parse_mode="Markdown"
        )
        
        # Reset states
        if cid in user_lms_escalation_attempts:
            user_lms_escalation_attempts[cid] = {"count": 0, "issue": ""}
        del user_lms_detail_collection[cid]
        
        send_support_menu(bot, cid)
    
    return True


def send_lms_escalation_email(name, email, bfsi_id, issue, username, user_id):
    """Send LMS escalation email to IT team."""
    try:
        send_email_to_it(f"{name} ({email})", f"LMS / Videos - {issue}")
        print(f"📧 LMS Escalation email sent for {name} ({email})")
    except Exception as e:
        print(f"❌ Email error: {e}")


def is_in_lms_other_mode(chat_id):
    """Check if user is in 'Other LMS Issue' mode."""
    return user_lms_other_mode.get(chat_id, False)


def handle_lms_other_message(bot, message):
    """Handle free-text input for 'Other LMS Issue'."""
    cid = message.chat.id
    user_query = message.text

    bot.send_chat_action(cid, "typing")
    
    # Use AI to respond to LMS issue
    prompt = f"User is facing an LMS/Video issue on Skillserv portal. Their issue: {user_query}"
    ai_response = ask_ai_free(prompt)
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("✅ Issue Resolved", callback_data="lms_fixed"),
        types.InlineKeyboardButton("❓ Still Need Help", callback_data="lms_still_not_working"),
        types.InlineKeyboardButton("⬅️ Back to LMS Menu", callback_data="lms")
    )
    
    bot.send_message(cid, ai_response, reply_markup=markup)
    
    # Clear the mode
    user_lms_other_mode[cid] = False
