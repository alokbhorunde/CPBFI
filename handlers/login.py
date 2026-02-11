from telebot import types
from handlers.menu import send_support_menu
from utils.ai import ask_ai_free
from utils.email import send_email_to_it

user_login_other_mode = {}
user_escalation_attempts = {}
user_detail_collection = {}


def register(bot):
    """Register all login-related callback handlers."""

    @bot.callback_query_handler(func=lambda call: call.data.startswith("login"))
    def handle_login(call):
        cid = call.message.chat.id
        data = call.data

        if data == "login":
            user_escalation_attempts[cid] = user_escalation_attempts.get(cid, {"count": 0, "portal": "", "issue": ""})

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Skillserv Portal", callback_data="login_portal_skillserv"),
                types.InlineKeyboardButton("Knowlens Portal", callback_data="login_portal_knowlens"),
                types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="login_back_menu")
            )

            bot.send_message(cid,
                "**Login Issue**\n\n"
                "Which portal are you trying to log in to?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data in ["login_portal_skillserv", "login_portal_knowlens"]:
            portal = "Skillserv" if "skillserv" in data else "Knowlens"

            if cid not in user_escalation_attempts:
                user_escalation_attempts[cid] = {"count": 0, "portal": portal, "issue": ""}
            else:
                user_escalation_attempts[cid]["portal"] = portal

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Invalid / Wrong Credentials", callback_data=f"login_creds_{portal.lower()}"),
                types.InlineKeyboardButton("OTP Not Received", callback_data=f"login_otp_{portal.lower()}"),
                types.InlineKeyboardButton("Forgot Password Issue", callback_data=f"login_forgot_{portal.lower()}"),
                types.InlineKeyboardButton("Other Login Issue", callback_data=f"login_other_{portal.lower()}"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="login")
            )

            bot.send_message(cid,
                f"**{portal} Portal — Login Help**\n\n"
                "What issue are you facing while logging in?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data.startswith("login_creds_"):
            portal = data.split("_")[-1].capitalize()
            track_issue(cid, portal, "Invalid/Wrong Credentials")

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Try Again", callback_data=f"login_portal_{portal.lower()}"),
                types.InlineKeyboardButton("Forgot Password", callback_data=f"login_forgot_{portal.lower()}"),
                types.InlineKeyboardButton("Still Not Working", callback_data=f"login_still_not_working_{portal.lower()}"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_portal_{portal.lower()}")
            )

            bot.send_message(cid,
                "**Invalid / Wrong Credentials**\n\n"
                "Please check the following carefully:\n\n"
                "1. Make sure you are entering the correct:\n"
                "   • Registered Email ID\n"
                "   • Password (check caps lock)\n\n"
                "2. Confirm you are using the same email ID used during registration.\n\n"
                "3. Try closing the browser tab completely and log in again.\n\n"
                "4. If possible, try logging in from another device or browser.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data.startswith("login_otp_"):
            portal = data.split("_")[-1].capitalize()
            track_issue(cid, portal, "OTP Not Received")

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Still Not Received", callback_data=f"login_still_not_working_{portal.lower()}"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_portal_{portal.lower()}"),
                types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="login_back_menu")
            )

            bot.send_message(cid,
                "**OTP Not Received**\n\n"
                "Please try the following steps:\n\n"
                "1. Check your **Spam / Junk** folder.\n"
                "2. Wait **2–3 minutes**, then refresh the login page and request a new OTP.\n"
                "3. Do **NOT** request OTP multiple times in a short duration.\n"
                "4. Try a different browser (Chrome, Edge, Firefox).\n"
                "5. Try a different device (phone, tablet, laptop).\n"
                "6. Ensure you're on a stable internet connection.\n\n"
                "_Requesting too many OTPs may temporarily block delivery._",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data.startswith("login_still_not_working_"):
            portal = data.split("_")[-1].capitalize()

            if cid not in user_escalation_attempts:
                user_escalation_attempts[cid] = {"count": 1, "portal": portal, "issue": "Login Issue"}
            else:
                user_escalation_attempts[cid]["count"] += 1

            attempts = user_escalation_attempts[cid]["count"]

            if attempts >= 2:
                start_detail_collection(bot, cid, portal, user_escalation_attempts[cid].get("issue", "Login Issue"))
            else:
                markup = types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    types.InlineKeyboardButton("Try Again", callback_data=f"login_portal_{portal.lower()}"),
                    types.InlineKeyboardButton("Still Not Working", callback_data=f"login_still_not_working_{portal.lower()}")
                )

                bot.send_message(cid,
                    "**Let's try once more**\n\n"
                    "Please try the following:\n"
                    "1. Clear your browser cache\n"
                    "2. Try in Incognito/Private mode\n"
                    "3. Use a different browser or device\n\n"
                    f"_Attempt {attempts}/2 - After 2 attempts, we'll connect you with support._",
                    parse_mode="Markdown",
                    reply_markup=markup
                )

        elif data.startswith("login_forgot_") and not data.startswith("login_forgot_retry_") and not data.startswith("login_forgot_otp_"):
            portal = data.split("_")[-1].capitalize()
            track_issue(cid, portal, "Forgot Password")

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Try Again", callback_data=f"login_forgot_retry_{portal.lower()}"),
                types.InlineKeyboardButton("OTP / Reset Link Not Received", callback_data=f"login_forgot_otp_{portal.lower()}"),
                types.InlineKeyboardButton("Still Facing Issue", callback_data=f"login_still_not_working_{portal.lower()}"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_portal_{portal.lower()}")
            )

            bot.send_message(cid,
                f"**Forgot Password — {portal}**\n\n"
                "Please make sure:\n\n"
                "1. You selected the correct portal:\n"
                f"   • **{portal}**\n\n"
                "2. You entered the **registered email ID**.\n\n"
                "3. Check **Spam / Junk** folder for reset email.\n\n"
                "4. Close the browser window and try again after a few minutes.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data.startswith("login_forgot_retry_"):
            portal = data.split("_")[-1].capitalize()

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("✅ Worked!", callback_data="login_fixed"),
                types.InlineKeyboardButton("Still Facing Issue", callback_data=f"login_still_not_working_{portal.lower()}"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_forgot_{portal.lower()}")
            )

            bot.send_message(cid,
                "**Try Again**\n\n"
                "1. Close all browser tabs\n"
                "2. Clear browser cache\n"
                "3. Go to the login page again\n"
                "4. Click 'Forgot Password'\n"
                "5. Enter your registered email ID carefully",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data.startswith("login_forgot_otp_"):
            portal = data.split("_")[-1].capitalize()

            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("Resend Reset Link", callback_data=f"login_forgot_retry_{portal.lower()}"),
                types.InlineKeyboardButton("Still Not Received", callback_data=f"login_still_not_working_{portal.lower()}"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_forgot_{portal.lower()}")
            )

            bot.send_message(cid,
                "**Reset Link / OTP Not Received**\n\n"
                "Please check:\n\n"
                "1. Check your **Spam / Junk** folder\n"
                "2. Wait **2–3 minutes** before requesting again\n"
                "3. Ensure you entered the correct email ID\n\n"
                "_Too many requests may temporarily block delivery._",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data.startswith("login_other_"):
            portal = data.split("_")[-1].capitalize()
            user_login_other_mode[cid] = portal
            track_issue(cid, portal, "Other Login Issue")

            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_portal_{portal.lower()}"))

            bot.send_message(cid,
                f"**Other Login Issue — {portal}**\n\n"
                "Please briefly describe the login issue you are facing.\n"
                "Our AI will analyze and provide help.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "login_fixed":
            if cid in user_escalation_attempts:
                user_escalation_attempts[cid] = {"count": 0, "portal": "", "issue": ""}

            bot.send_message(cid, "Great! Your login issue is resolved.\n\nHappy learning!")
            send_support_menu(bot, cid)

        elif data == "login_back_menu":
            send_support_menu(bot, cid)


def track_issue(cid, portal, issue):
    if cid not in user_escalation_attempts:
        user_escalation_attempts[cid] = {"count": 0, "portal": portal, "issue": issue}
    else:
        user_escalation_attempts[cid]["portal"] = portal
        user_escalation_attempts[cid]["issue"] = issue


def start_detail_collection(bot, cid, portal, issue):
    user_detail_collection[cid] = {
        "step": "name",
        "name": "",
        "email": "",
        "bfsi": "",
        "issue": issue,
        "portal": portal
    }

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="login"))

    bot.send_message(cid,
        "**Escalating to Support Team**\n\n"
        "We need a few details to help you faster.\n\n"
        "**Step 1/3:** Please enter your **Full Name**:",
        parse_mode="Markdown",
        reply_markup=markup
    )


def is_in_detail_collection_mode(chat_id):
    return chat_id in user_detail_collection and user_detail_collection[chat_id].get("step") is not None


def handle_detail_collection(bot, message):
    cid = message.chat.id
    user_input = message.text.strip()

    if cid not in user_detail_collection:
        return False

    current_step = user_detail_collection[cid]["step"]

    if current_step == "name":
        user_detail_collection[cid]["name"] = user_input
        user_detail_collection[cid]["step"] = "email"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="login"))

        bot.send_message(cid,
            f"Name: **{user_input}**\n\n"
            "**Step 2/3:** Please enter your **Email ID**:",
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif current_step == "email":
        user_detail_collection[cid]["email"] = user_input
        user_detail_collection[cid]["step"] = "bfsi"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("❌ Cancel", callback_data="login"))

        bot.send_message(cid,
            f"Email: **{user_input}**\n\n"
            "**Step 3/3:** Please enter your **BFSI ID**:",
            parse_mode="Markdown",
            reply_markup=markup
        )

    elif current_step == "bfsi":
        user_detail_collection[cid]["bfsi"] = user_input
        user_detail_collection[cid]["step"] = None

        details = user_detail_collection[cid]

        send_login_escalation_email(
            name=details["name"],
            email=details["email"],
            bfsi_id=details["bfsi"],
            portal=details["portal"],
            issue=details["issue"]
        )

        bot.send_message(cid,
            "**Issue Escalated Successfully!**\n\n"
            f"**Details Submitted:**\n"
            f"• Name: {details['name']}\n"
            f"• Email: {details['email']}\n"
            f"• BFSI ID: {details['bfsi']}\n"
            f"• Portal: {details['portal']}\n"
            f"• Issue: {details['issue']}\n\n"
            "Our support team will contact you shortly.\n"
            "For urgent queries: support@cpbfi.org\n\n"
            "Thank you for your patience!",
            parse_mode="Markdown"
        )

        if cid in user_escalation_attempts:
            user_escalation_attempts[cid] = {"count": 0, "portal": "", "issue": ""}
        del user_detail_collection[cid]

        send_support_menu(bot, cid)

    return True


def send_login_escalation_email(name, email, bfsi_id, portal, issue):
    try:
        send_email_to_it(f"{name} ({email})", f"LOGIN - {issue} - {portal}")
        print(f"Login escalation email sent for {name} ({email})")
    except Exception as e:
        print(f"Email error: {e}")


def is_in_login_other_mode(chat_id):
    return user_login_other_mode.get(chat_id) is not None


def handle_login_other_message(bot, message):
    cid = message.chat.id
    portal = user_login_other_mode.get(cid)
    user_query = message.text

    bot.send_chat_action(cid, "typing")

    prompt = f"User is facing a login issue on {portal} portal. Their issue: {user_query}"
    ai_response = ask_ai_free(prompt)

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("✅ Issue Resolved", callback_data="login_fixed"),
        types.InlineKeyboardButton("Still Need Help", callback_data=f"login_still_not_working_{portal.lower()}"),
        types.InlineKeyboardButton("⬅️ Back to Login Menu", callback_data="login")
    )

    bot.send_message(cid, ai_response, reply_markup=markup, parse_mode="Markdown")

    user_login_other_mode[cid] = None


def get_login_other_portal(chat_id):
    return user_login_other_mode.get(chat_id)
