import logging
from telebot import types
from handlers.menu import send_support_menu
from utils.ai import ask_ai_free
from utils.email import send_email_to_it
from utils.validators import is_valid_email

logger = logging.getLogger(__name__)

user_assessment_other_mode = {}
user_assessment_escalation_attempts = {}
user_assessment_detail_collection = {}


def register(bot):
    """Register all assessment-related callback handlers."""

    @bot.callback_query_handler(func=lambda call: call.data.startswith("assessment") or call.data.startswith("pcq") or call.data.startswith("post"))
    def handle_assessment(call):
        bot.answer_callback_query(call.id)
        cid = call.message.chat.id
        data = call.data

        if data == "assessment":
            # Clear any in-progress detail collection when returning to menu
            if cid in user_assessment_detail_collection:
                del user_assessment_detail_collection[cid]

            if cid not in user_assessment_escalation_attempts:
                user_assessment_escalation_attempts[cid] = {"count": 0, "issue": "", "type": ""}

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Pre-Course Quiz (PCQ)", callback_data="assessment_pcq"),
                types.InlineKeyboardButton("Post Assessment", callback_data="assessment_post"),
                types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Assessment Issues — Skillserv Portal**\n\n"
                "Which type of assessment are you facing issues with?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data in ("assessment_pcq", "pcq"):
            if cid not in user_assessment_escalation_attempts:
                user_assessment_escalation_attempts[cid] = {"count": 0, "issue": "", "type": "PCQ"}
            else:
                user_assessment_escalation_attempts[cid]["type"] = "PCQ"

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Where is the Quiz?", callback_data="pcq_where"),
                types.InlineKeyboardButton("Test Not Showing", callback_data="pcq_not_showing"),
                types.InlineKeyboardButton("Unable to Submit", callback_data="pcq_submit"),
                types.InlineKeyboardButton("Exited Midway", callback_data="pcq_exited"),
                types.InlineKeyboardButton("Joined Late", callback_data="pcq_time"),
                types.InlineKeyboardButton("Other PCQ Issue", callback_data="pcq_other"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment")
            )

            bot.send_message(cid,
                "**Pre-Course Quiz (PCQ) Issue**\n\n"
                "What PCQ-related issue are you facing?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "pcq_where":
            track_assessment_issue(cid, "Where is the Quiz", "PCQ")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Still Not Visible", callback_data="assessment_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment_pcq"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Where is the Quiz?**\n\n"
                "To access the PCQ quiz on Skillserv:\n\n"
                "1. Login to the Skillserv portal.\n"
                "2. Go to your dashboard.\n"
                "3. Look for the PCQ / Assessment section.\n"
                "4. Click on the active quiz link.\n"
                "5. If not visible, press Ctrl+F5 to hard refresh.\n"
                "6. Or close and reopen the browser, then login again.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "pcq_not_showing":
            track_assessment_issue(cid, "Test Not Showing", "PCQ")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Tried All Steps", callback_data="assessment_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment_pcq"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Test Not Showing**\n\n"
                "If the PCQ test is not showing, please try the following:\n\n"
                "1. Refresh the page once.\n"
                "2. Ensure you are logged in using the registered email ID.\n"
                "3. Close the browser tab and login again.\n"
                "4. Try accessing the portal from another device or browser.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "pcq_submit":
            track_assessment_issue(cid, "Unable to Submit", "PCQ")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Still Unable to Submit", callback_data="assessment_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment_pcq"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Unable to Submit**\n\n"
                "If you are unable to submit the PCQ:\n\n"
                "1. Ensure all questions are attempted.\n"
                "2. Check your internet connection.\n"
                "3. Wait for a few seconds and try submitting again.\n"
                "4. Avoid refreshing the page repeatedly.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "pcq_exited":
            track_assessment_issue(cid, "Exited Midway", "PCQ")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Cannot Rejoin", callback_data="assessment_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment_pcq"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Exited Midway**\n\n"
                "If you exited the PCQ midway:\n\n"
                "1. Login again and check if the quiz resumes automatically.\n"
                "2. In most cases, re-entry depends on system rules.\n\n"
                "If the test does not resume, you may need support assistance.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "pcq_time":
            track_assessment_issue(cid, "Joined Late", "PCQ")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Talk to Support", callback_data="assessment_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment_pcq"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Joined Late**\n\n"
                "Since you joined late, you won't be able to access the exam.\n\n"
                "The PCQ is only accessible during the scheduled time window. "
                "Late entries are not permitted by the system.\n\n"
                "If you believe this is an error, you can talk to our support team.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "pcq_other":
            user_assessment_other_mode[cid] = {"active": True, "type": "PCQ"}
            track_assessment_issue(cid, "Other PCQ Issue", "PCQ")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment_pcq"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Other PCQ Issue**\n\n"
                "Please briefly describe the PCQ issue you are facing.\n"
                "Our AI will analyze and provide help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data in ("assessment_post", "post"):
            if cid not in user_assessment_escalation_attempts:
                user_assessment_escalation_attempts[cid] = {"count": 0, "issue": "", "type": "Post Assessment"}
            else:
                user_assessment_escalation_attempts[cid]["type"] = "Post Assessment"

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Assessment Not Visible", callback_data="post_not_visible"),
                types.InlineKeyboardButton("Test Not Loading", callback_data="post_not_loading"),
                types.InlineKeyboardButton("Unable to Submit", callback_data="post_submit"),
                types.InlineKeyboardButton("Exited Midway", callback_data="post_exited"),
                types.InlineKeyboardButton("Time Window Issue", callback_data="post_time"),
                types.InlineKeyboardButton("Other Post Assessment Issue", callback_data="post_other"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment")
            )

            bot.send_message(cid,
                "**Post Assessment Issue**\n\n"
                "What Post Assessment issue are you facing?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "post_not_visible":
            track_assessment_issue(cid, "Assessment Not Visible", "Post Assessment")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Still Not Visible", callback_data="assessment_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment_post"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Assessment Not Visible**\n\n"
                "To access the Post Assessment on Skillserv:\n\n"
                "1. Login to the Skillserv portal.\n"
                "2. Go to your dashboard.\n"
                "3. Look for the Assessment / Test section.\n"
                "4. Ensure the assessment time window is active.\n"
                "5. Press Ctrl+F5 to hard refresh.\n"
                "6. Or close and reopen the browser, then login again.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "post_not_loading":
            track_assessment_issue(cid, "Test Not Loading", "Post Assessment")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Tried All Steps", callback_data="assessment_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment_post"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Test Not Loading**\n\n"
                "If the Post Assessment is not loading, please try:\n\n"
                "1. Refresh the page once.\n"
                "2. Clear browser cache and cookies.\n"
                "3. Try in Incognito/Private mode.\n"
                "4. Try accessing from another device or browser.\n"
                "5. Check your internet connection.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "post_submit":
            track_assessment_issue(cid, "Unable to Submit", "Post Assessment")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Still Unable to Submit", callback_data="assessment_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment_post"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Unable to Submit**\n\n"
                "If you are unable to submit the Post Assessment:\n\n"
                "1. Ensure all questions are attempted.\n"
                "2. Check your internet connection.\n"
                "3. Wait for a few seconds and try submitting again.\n"
                "4. Avoid refreshing the page repeatedly.\n"
                "5. Check if you are within the allowed time window.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "post_exited":
            track_assessment_issue(cid, "Exited Midway", "Post Assessment")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Cannot Rejoin", callback_data="assessment_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment_post"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Exited Midway**\n\n"
                "If you exited the Post Assessment midway:\n\n"
                "1. Login again and check if the test resumes automatically.\n"
                "2. In most cases, re-entry depends on system rules.\n\n"
                "If the test does not resume, you may need support assistance.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "post_time":
            track_assessment_issue(cid, "Time Window Issue", "Post Assessment")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("Still Facing Issue", callback_data="assessment_still_not_working")
            )
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment_post"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Time Window Issue**\n\n"
                "Post Assessments are only accessible within a specific time window.\n\n"
                "Please check:\n"
                "1. Is your assessment time window currently active?\n"
                "2. Check the scheduled time in your course calendar.\n"
                "3. Ensure you are attempting within the allowed hours.\n"
                "4. If active, try refreshing the page (Ctrl+F5).\n"
                "5. Clear browser cache and try a different browser.\n\n"
                "Select an option below if you need further help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "post_other":
            user_assessment_other_mode[cid] = {"active": True, "type": "Post Assessment"}
            track_assessment_issue(cid, "Other Post Assessment Issue", "Post Assessment")

            markup = types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                types.InlineKeyboardButton("⬅️ Back", callback_data="assessment_post"),
                types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
            )

            bot.send_message(cid,
                "**Other Post Assessment Issue**\n\n"
                "Please briefly describe the Post Assessment issue you are facing.\n"
                "Our AI will analyze and provide help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data in ("assessment_still_not_working", "pcq_still_not_working"):
            if cid not in user_assessment_escalation_attempts:
                user_assessment_escalation_attempts[cid] = {"count": 1, "issue": "Assessment Issue", "type": ""}
            else:
                user_assessment_escalation_attempts[cid]["count"] += 1

            attempts = user_assessment_escalation_attempts[cid]["count"]
            assessment_type = user_assessment_escalation_attempts[cid].get("type", "Assessment")

            if attempts >= 2:
                start_assessment_detail_collection(
                    bot, cid,
                    user_assessment_escalation_attempts[cid].get("issue", "Assessment Issue"),
                    assessment_type
                )
            else:
                back_callback = "assessment_pcq" if assessment_type == "PCQ" else "assessment_post"

                markup = types.InlineKeyboardMarkup(row_width=2)
                markup.add(
                    types.InlineKeyboardButton("Still Not Working", callback_data="assessment_still_not_working")
                )
                markup.add(
                    types.InlineKeyboardButton("⬅️ Back", callback_data=back_callback),
                    types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
                )

                bot.send_message(cid,
                    "**Let's try once more**\n\n"
                    "Please try the following:\n"
                    "1. Clear your browser cache\n"
                    "2. Try in Incognito/Private mode\n"
                    "3. Use a different browser or device\n\n"
                    f"_Attempt {attempts}/2 - After 2 attempts, we'll connect you with support._\n\n"
                    "Select an option below if you need further help.",
                    parse_mode="Markdown",
                    reply_markup=markup
                )

        elif data in ("assessment_fixed", "pcq_fixed", "post_fixed"):
            if cid in user_assessment_escalation_attempts:
                user_assessment_escalation_attempts[cid] = {"count": 0, "issue": "", "type": ""}

            bot.send_message(cid, "Great! Your assessment issue is resolved.\n\nBest of luck with your assessment!")
            send_support_menu(bot, cid)

        elif data in ("assessment_back_menu", "pcq_back_menu"):
            send_support_menu(bot, cid)


def track_assessment_issue(cid, issue, assessment_type):
    if cid not in user_assessment_escalation_attempts:
        user_assessment_escalation_attempts[cid] = {"count": 0, "issue": issue, "type": assessment_type}
    else:
        user_assessment_escalation_attempts[cid]["issue"] = issue
        user_assessment_escalation_attempts[cid]["type"] = assessment_type


def start_assessment_detail_collection(bot, cid, issue, assessment_type):
    user_assessment_detail_collection[cid] = {
        "step": "describe",
        "description": "",
        "name": "",
        "email": "",
        "bfsi": "",
        "issue": issue,
        "type": assessment_type
    }

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="assessment"))

    bot.send_message(cid,
        f"**Escalating {assessment_type} Issue to Support Team**\n\n"
        "Before we connect you with support, please **briefly describe what exactly happened** "
        "and what you already tried.\n\n"
        "_Example: I refreshed the page and tried incognito mode but the quiz still shows 'Not Available'._",
        parse_mode="Markdown",
        reply_markup=markup
    )


def is_in_assessment_detail_collection_mode(chat_id):
    return chat_id in user_assessment_detail_collection and user_assessment_detail_collection[chat_id].get("step") is not None


def handle_assessment_detail_collection(bot, message):
    cid = message.chat.id
    user_input = message.text.strip()

    if cid not in user_assessment_detail_collection:
        return False

    current_step = user_assessment_detail_collection[cid]["step"]
    assessment_type = user_assessment_detail_collection[cid].get("type", "Assessment")

    if current_step == "describe":
        user_assessment_detail_collection[cid]["description"] = user_input
        user_assessment_detail_collection[cid]["step"] = "name"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="assessment"))

        bot.send_message(cid,
            "Got it. Now we need a few details to help you.\n\n"
            "**Step 1/3:** Please enter your **Full Name**:",
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif current_step == "name":
        user_assessment_detail_collection[cid]["name"] = user_input
        user_assessment_detail_collection[cid]["step"] = "email"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="assessment"))

        bot.send_message(cid,
            f"Name: **{user_input}**\n\n"
            "**Step 2/3:** Please enter your **Email ID**:",
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif current_step == "email":
        if not is_valid_email(user_input):
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="assessment"))

            bot.send_message(cid,
                "⚠️ That doesn't look like a valid email address.\n\n"
                "Please enter a valid **Email ID** (e.g. name@example.com):",
                parse_mode="Markdown",
                reply_markup=markup
            )
            return True

        user_assessment_detail_collection[cid]["email"] = user_input
        user_assessment_detail_collection[cid]["step"] = "bfsi"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="assessment"))

        bot.send_message(cid,
            f"Email: **{user_input}**\n\n"
            "**Step 3/3:** Please enter your **BFSI ID**:",
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif current_step == "bfsi":
        user_assessment_detail_collection[cid]["bfsi"] = user_input
        user_assessment_detail_collection[cid]["step"] = None

        details = user_assessment_detail_collection[cid]

        email_sent = send_assessment_escalation_email(
            name=details["name"],
            email=details["email"],
            bfsi_id=details["bfsi"],
            issue=details["issue"],
            assessment_type=details["type"],
            username=message.from_user.username or "N/A",
            user_id=message.from_user.id,
            description=details.get("description", "")
        )

        if email_sent:
            bot.send_message(cid,
                f"**{assessment_type} Issue Escalated Successfully!**\n\n"
                f"**Details Submitted:**\n"
                f"• Name: {details['name']}\n"
                f"• Email: {details['email']}\n"
                f"• BFSI ID: {details['bfsi']}\n"
                f"• Portal: Skillserv\n"
                f"• Assessment Type: {details['type']}\n"
                f"• Issue: {details['issue']}\n"
                f"• Description: {details['description']}\n\n"
                "Our support team will contact you shortly.\n"
                "For urgent queries: support@cpbfi.org\n\n"
                "Thank you for your patience!",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(cid,
                f"**{assessment_type} Issue Recorded — Email Could Not Be Sent**\n\n"
                f"**Your Details:**\n"
                f"• Name: {details['name']}\n"
                f"• Email: {details['email']}\n"
                f"• BFSI ID: {details['bfsi']}\n"
                f"• Assessment Type: {details['type']}\n"
                f"• Issue: {details['issue']}\n\n"
                "⚠️ We couldn't send the escalation email automatically.\n"
                "Please contact support directly: **support@cpbfi.org**",
                parse_mode="Markdown"
            )

        if cid in user_assessment_escalation_attempts:
            user_assessment_escalation_attempts[cid] = {"count": 0, "issue": "", "type": ""}
        del user_assessment_detail_collection[cid]

        send_support_menu(bot, cid)

    return True


def send_assessment_escalation_email(name, email, bfsi_id, issue, assessment_type, username, user_id, description=""):
    """Returns True if email sent, False if failed."""
    issue_detail = f"{assessment_type} - {issue} - Skillserv\n\nStudent Description: {description}"
    return send_email_to_it(f"{name} ({email})", issue_detail)


def is_in_assessment_other_mode(chat_id):
    mode_data = user_assessment_other_mode.get(chat_id, {})
    return mode_data.get("active", False) if isinstance(mode_data, dict) else False


def handle_assessment_other_message(bot, message):
    cid = message.chat.id
    user_query = message.text

    bot.send_chat_action(cid, "typing")

    mode_data = user_assessment_other_mode.get(cid, {})
    assessment_type = mode_data.get("type", "Assessment") if isinstance(mode_data, dict) else "Assessment"

    prompt = f"User is facing a {assessment_type} issue on Skillserv portal. Their issue: {user_query}"
    ai_response = ask_ai_free(prompt)

    back_callback = "assessment_pcq" if assessment_type == "PCQ" else "assessment_post"

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Issue Resolved", callback_data="assessment_fixed"),
        types.InlineKeyboardButton("Still Need Help", callback_data="assessment_still_not_working")
    )
    markup.add(
        types.InlineKeyboardButton("⬅️ Back", callback_data=back_callback),
        types.InlineKeyboardButton("⬅️ Main Menu", callback_data="assessment_back_menu")
    )

    bot.send_message(cid, ai_response, reply_markup=markup, parse_mode="Markdown")

    user_assessment_other_mode[cid] = {"active": False, "type": ""}
