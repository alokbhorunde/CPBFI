from telebot import types
from handlers.menu import send_support_menu
from utils.ai import ask_ai_free
from utils.email import send_email_to_it

user_lms_other_mode = {}
user_lms_escalation_attempts = {}
user_lms_detail_collection = {}


def register(bot):
    """Register all LMS-related callback handlers."""

    @bot.callback_query_handler(func=lambda call: call.data.startswith("lms"))
    def handle_lms(call):
        cid = call.message.chat.id
        data = call.data

        if data == "lms":
            user_lms_escalation_attempts[cid] = {"count": 0, "issue": ""}

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Batch Videos Not Visible", callback_data="lms_videos_not_visible"),
                types.InlineKeyboardButton("Videos Not Playing", callback_data="lms_videos_not_playing"),
                types.InlineKeyboardButton("Progress / Completion Not Updated", callback_data="lms_progress"),
                types.InlineKeyboardButton("Course Expired / Access Duration", callback_data="lms_expired"),
                types.InlineKeyboardButton("Other LMS Issue", callback_data="lms_other"),
                types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="lms_back_menu")
            )

            bot.send_message(cid,
                "**LMS / Videos Issue**\n\n"
                "Please select the LMS-related issue you are facing:",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "lms_videos_not_visible":
            track_lms_issue(cid, "Batch Videos Not Visible")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Still Not Visible", callback_data="lms_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="lms"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="lms_back_menu")
            )

            bot.send_message(cid,
                "**Batch Videos Not Visible**\n\n"
                "If batch launch videos are not visible on your dashboard, please note:\n\n"
                "1. Batch videos are assigned only after batch launch.\n"
                "2. System sync may take some time after launch.\n"
                "3. Log out and log in again.\n"
                "4. Refresh your dashboard and check for updates.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "lms_videos_not_playing":
            track_lms_issue(cid, "Videos Not Playing")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Tried All Steps", callback_data="lms_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="lms"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="lms_back_menu")
            )

            bot.send_message(cid,
                "**Videos Not Playing**\n\n"
                "If videos are not playing on the LMS, try the following steps:\n\n"
                "1. Use Google Chrome browser (recommended).\n"
                "2. Check your internet connection.\n"
                "3. Refresh the page once.\n"
                "4. Clear browser cache if required.\n"
                "5. Log out and log in again before retrying.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "lms_progress":
            track_lms_issue(cid, "Progress / Completion Not Updated")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Still Not Updated", callback_data="lms_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="lms"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="lms_back_menu")
            )

            bot.send_message(cid,
                "**Progress / Completion Not Updated**\n\n"
                "If your learning progress or completion status is not updating:\n\n"
                "1. LMS progress may take time to sync with the portal.\n"
                "2. Ensure all required videos/modules are completed.\n"
                "3. Follow the learning sequence strictly.\n"
                "4. Avoid skipping videos.\n"
                "5. Log out and log in again after some time.\n"
                "6. Refresh the dashboard.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "lms_expired":
            track_lms_issue(cid, "Course Expired / Access Duration")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Still Have a Question", callback_data="lms_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="lms"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="lms_back_menu")
            )

            bot.send_message(cid,
                "**Course Expired / LMS Access Duration**\n\n"
                "Regarding LMS content access:\n\n"
                "LMS access is available for **30 to 45 days** from the batch launch date.\n\n"
                "After this period, course content may show as expired.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "lms_other":
            user_lms_other_mode[cid] = True
            track_lms_issue(cid, "Other LMS Issue")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="lms"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="lms_back_menu")
            )

            bot.send_message(cid,
                "**Other LMS Issue**\n\n"
                "Please briefly describe the LMS issue you are facing.\n"
                "Our support team will review it.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "lms_still_not_working":
            if cid not in user_lms_escalation_attempts:
                user_lms_escalation_attempts[cid] = {"count": 1, "issue": "LMS Issue"}
            else:
                user_lms_escalation_attempts[cid]["count"] += 1

            attempts = user_lms_escalation_attempts[cid]["count"]

            if attempts >= 2:
                start_lms_detail_collection(bot, cid, user_lms_escalation_attempts[cid].get("issue", "LMS Issue"))
            else:
                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("Still Not Working", callback_data="lms_still_not_working")
                )
                markup.add(
                    types.InlineKeyboardButton("⬅️ Back", callback_data="lms"),
                    types.InlineKeyboardButton("⬅️ Main Menu", callback_data="lms_back_menu")
                )

                bot.send_message(cid,
                    "**Let's try once more**\n\n"
                    "Please try the following:\n"
                    "1. Clear your browser cache\n"
                    "2. Try in Incognito/Private mode\n"
                    "3. Use a different browser (Chrome recommended)\n"
                    "4. Check your internet connection\n\n"
                    f"_Attempt {attempts}/2 - After 2 attempts, we'll connect you with support._\n\n"
                    "Select an option below if you need further help.",
                    parse_mode="Markdown",
                    reply_markup=markup
                )

        elif data == "lms_fixed":
            if cid in user_lms_escalation_attempts:
                user_lms_escalation_attempts[cid] = {"count": 0, "issue": ""}

            bot.send_message(cid, "Great! Your LMS issue is resolved.\n\nHappy learning!")
            send_support_menu(bot, cid)

        elif data == "lms_back_menu":
            send_support_menu(bot, cid)


def track_lms_issue(cid, issue):
    if cid not in user_lms_escalation_attempts:
        user_lms_escalation_attempts[cid] = {"count": 0, "issue": issue}
    else:
        user_lms_escalation_attempts[cid]["issue"] = issue


def start_lms_detail_collection(bot, cid, issue):
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
        "**Escalating LMS Issue to Support Team**\n\n"
        "We need a few details to help you faster.\n\n"
        "**Step 1/3:** Please enter your **Full Name**:",
        parse_mode="Markdown",
        reply_markup=markup
    )


def is_in_lms_detail_collection_mode(chat_id):
    return chat_id in user_lms_detail_collection and user_lms_detail_collection[chat_id].get("step") is not None


def handle_lms_detail_collection(bot, message):
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
            f"Name: **{user_input}**\n\n"
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
            f"Email: **{user_input}**\n\n"
            "**Step 3/3:** Please enter your **BFSI ID**:",
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif current_step == "bfsi":
        user_lms_detail_collection[cid]["bfsi"] = user_input
        user_lms_detail_collection[cid]["step"] = None

        details = user_lms_detail_collection[cid]

        send_lms_escalation_email(
            name=details["name"],
            email=details["email"],
            bfsi_id=details["bfsi"],
            issue=details["issue"],
            username=message.from_user.username or "N/A",
            user_id=message.from_user.id
        )

        bot.send_message(cid,
            "**LMS Issue Escalated Successfully!**\n\n"
            f"**Details Submitted:**\n"
            f"• Name: {details['name']}\n"
            f"• Email: {details['email']}\n"
            f"• BFSI ID: {details['bfsi']}\n"
            f"• Issue Type: LMS / Videos\n"
            f"• Issue: {details['issue']}\n\n"
            "Our support team will contact you shortly.\n"
            "For urgent queries: support@cpbfi.org\n\n"
            "Please allow some time for review. Thank you!",
            parse_mode="Markdown"
        )

        if cid in user_lms_escalation_attempts:
            user_lms_escalation_attempts[cid] = {"count": 0, "issue": ""}
        del user_lms_detail_collection[cid]

        send_support_menu(bot, cid)

    return True


def send_lms_escalation_email(name, email, bfsi_id, issue, username, user_id):
    try:
        send_email_to_it(f"{name} ({email})", f"LMS / Videos - {issue}")
        print(f"LMS escalation email sent for {name} ({email})")
    except Exception as e:
        print(f"Email error: {e}")


def is_in_lms_other_mode(chat_id):
    return user_lms_other_mode.get(chat_id, False)


def handle_lms_other_message(bot, message):
    cid = message.chat.id
    user_query = message.text

    bot.send_chat_action(cid, "typing")

    prompt = f"User is facing an LMS/Video issue on Skillserv portal. Their issue: {user_query}"
    ai_response = ask_ai_free(prompt)

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Issue Resolved", callback_data="lms_fixed"),
        types.InlineKeyboardButton("Still Need Help", callback_data="lms_still_not_working")
    )
    markup.add(
        types.InlineKeyboardButton("⬅️ Back", callback_data="lms"),
        types.InlineKeyboardButton("⬅️ Main Menu", callback_data="lms_back_menu")
    )

    bot.send_message(cid, ai_response, reply_markup=markup, parse_mode="Markdown")

    user_lms_other_mode[cid] = False
