from telebot import types
from handlers.menu import send_support_menu
from utils.ai import ask_ai_free

# State for "Other Login Issue" - free text input
user_login_other_mode = {}


def register(bot):
    """Register all login-related callback handlers."""
    
    @bot.callback_query_handler(func=lambda call: call.data.startswith("login"))
    def handle_login(call):
        cid = call.message.chat.id
        data = call.data

        # --------------------------------------------------
        # STEP 1: Portal Selection (Entry Point)
        # --------------------------------------------------
        if data == "login":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🟦 Skillserv Portal", callback_data="login_portal_skillserv"),
                types.InlineKeyboardButton("🟩 Knowlens Portal", callback_data="login_portal_knowlens"),
                types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="login_back_menu")
            )

            bot.send_message(cid,
                "🔐 **Login Issue**\n\n"
                "Which portal are you trying to log in to?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # --------------------------------------------------
        # STEP 2: Identify Login Problem (after portal selection)
        # --------------------------------------------------
        elif data in ["login_portal_skillserv", "login_portal_knowlens"]:
            portal = "Skillserv" if "skillserv" in data else "Knowlens"
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("❌ Invalid / Wrong Credentials", callback_data=f"login_creds_{portal.lower()}"),
                types.InlineKeyboardButton("📩 OTP Not Received", callback_data=f"login_otp_{portal.lower()}"),
                types.InlineKeyboardButton("🔑 Forgot Password Issue", callback_data=f"login_forgot_{portal.lower()}"),
                types.InlineKeyboardButton("❓ Other Login Issue", callback_data=f"login_other_{portal.lower()}"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="login")
            )

            bot.send_message(cid,
                f"🔐 **{portal} Portal — Login Help**\n\n"
                "What issue are you facing while logging in?",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # --------------------------------------------------
        # FLOW A: Invalid / Wrong Credentials
        # --------------------------------------------------
        elif data.startswith("login_creds_"):
            portal = data.split("_")[-1].capitalize()
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🔁 Try Again", callback_data=f"login_portal_{portal.lower()}"),
                types.InlineKeyboardButton("📩 Forgot Password", callback_data=f"login_forgot_{portal.lower()}"),
                types.InlineKeyboardButton("❓ Still Not Working (Talk to Support)", callback_data="login_escalate"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_portal_{portal.lower()}")
            )

            bot.send_message(cid,
                "❌ **Invalid / Wrong Credentials**\n\n"
                "Please check the following carefully:\n\n"
                "1️⃣ Make sure you are entering the correct:\n"
                "• Registered Email ID\n"
                "• Password (check caps lock)\n\n"
                "2️⃣ Confirm you are using the same email ID used during registration.\n\n"
                "3️⃣ Try closing the browser tab completely and log in again.\n\n"
                "4️⃣ If possible, try logging in from another device or browser.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # --------------------------------------------------
        # FLOW B: OTP Not Received
        # --------------------------------------------------
        elif data.startswith("login_otp_") and not data.startswith("login_otp_still_") and not data.startswith("login_otp_resend_") and not data.startswith("login_otp_confirm_"):
            portal = data.split("_")[-1].capitalize()
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("📤 Resend OTP (After Waiting)", callback_data=f"login_otp_resend_{portal.lower()}"),
                types.InlineKeyboardButton("🔄 Try Another Device / Browser", callback_data=f"login_otp_device_{portal.lower()}"),
                types.InlineKeyboardButton("❓ Still Not Received", callback_data=f"login_otp_still_{portal.lower()}"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_portal_{portal.lower()}")
            )

            bot.send_message(cid,
                "📩 **OTP Not Received**\n\n"
                "If you are not receiving the OTP, please check the following:\n\n"
                "1️⃣ Check your **Spam / Junk** folder.\n"
                "2️⃣ Wait for **2–3 minutes** before requesting again.\n"
                "3️⃣ Do **NOT** request OTP multiple times in a short duration.\n\n"
                "⚠️ *Requesting too many OTPs may temporarily block delivery.*",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # OTP Resend confirmation
        elif data.startswith("login_otp_resend_"):
            portal = data.split("_")[-1].capitalize()
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("✅ Done, Trying Again", callback_data=f"login_portal_{portal.lower()}"),
                types.InlineKeyboardButton("❓ Still Not Received", callback_data=f"login_otp_still_{portal.lower()}"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_otp_{portal.lower()}")
            )

            bot.send_message(cid,
                "📤 **Resend OTP**\n\n"
                "Please wait at least 2-3 minutes, then:\n"
                "1️⃣ Refresh the login page\n"
                "2️⃣ Request a new OTP\n"
                "3️⃣ Check both Inbox and Spam folder",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # OTP - Try another device
        elif data.startswith("login_otp_device_"):
            portal = data.split("_")[-1].capitalize()
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("✅ Worked!", callback_data="login_fixed"),
                types.InlineKeyboardButton("❓ Still Not Received", callback_data=f"login_otp_still_{portal.lower()}"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_otp_{portal.lower()}")
            )

            bot.send_message(cid,
                "🔄 **Try Another Device / Browser**\n\n"
                "Please try:\n"
                "• A different browser (Chrome, Edge, Firefox)\n"
                "• A different device (phone, tablet, laptop)\n"
                "• Ensure you're on a stable internet connection",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # OTP - Still not received (confirmation before escalation)
        elif data.startswith("login_otp_still_"):
            portal = data.split("_")[-1].capitalize()
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("✅ Yes, Confirm & Escalate", callback_data="login_otp_confirm_escalate"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_otp_{portal.lower()}")
            )

            bot.send_message(cid,
                "⚠️ **Before Escalating**\n\n"
                "Please confirm:\n\n"
                "✔ You entered the registered email ID\n"
                "✔ You waited at least 2–3 minutes\n"
                "✔ You did not request OTP multiple times",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # OTP - Confirm escalation
        elif data == "login_otp_confirm_escalate":
            bot.send_message(cid,
                "📞 **Escalated to Support**\n\n"
                "Your OTP issue has been noted.\n"
                "Our support team will look into this.\n\n"
                "📧 If urgent, please email: support@cpbfi.org\n\n"
                "Thank you for your patience! 🙏"
            )
            send_support_menu(bot, cid)

        # --------------------------------------------------
        # FLOW C: Forgot Password Issue
        # --------------------------------------------------
        elif data.startswith("login_forgot_") and not data.startswith("login_forgot_retry_") and not data.startswith("login_forgot_otp_"):
            portal = data.split("_")[-1].capitalize()
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("🔄 Try Again", callback_data=f"login_forgot_retry_{portal.lower()}"),
                types.InlineKeyboardButton("📩 OTP / Reset Link Not Received", callback_data=f"login_forgot_otp_{portal.lower()}"),
                types.InlineKeyboardButton("❓ Still Facing Issue", callback_data="login_escalate"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_portal_{portal.lower()}")
            )

            bot.send_message(cid,
                f"🔑 **Forgot Password — {portal}**\n\n"
                "Please make sure:\n\n"
                "1️⃣ You selected the correct portal:\n"
                f"• **{portal}**\n\n"
                "2️⃣ You entered the **registered email ID**.\n\n"
                "3️⃣ Check **Spam / Junk** folder for reset email.\n\n"
                "4️⃣ Close the browser window and try again after a few minutes.",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # Forgot password - Retry
        elif data.startswith("login_forgot_retry_"):
            portal = data.split("_")[-1].capitalize()
            
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("✅ Worked!", callback_data="login_fixed"),
                types.InlineKeyboardButton("❓ Still Facing Issue", callback_data=f"login_forgot_{portal.lower()}"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_forgot_{portal.lower()}")
            )

            bot.send_message(cid,
                "🔄 **Try Again**\n\n"
                "1️⃣ Close all browser tabs\n"
                "2️⃣ Clear browser cache\n"
                "3️⃣ Go to the login page again\n"
                "4️⃣ Click 'Forgot Password'\n"
                "5️⃣ Enter your registered email ID carefully",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # Forgot password - OTP/Reset link not received
        elif data.startswith("login_forgot_otp_"):
            portal = data.split("_")[-1].capitalize()
            
            # Redirect to OTP flow
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("📤 Resend Reset Link", callback_data=f"login_forgot_retry_{portal.lower()}"),
                types.InlineKeyboardButton("❓ Still Not Received (Escalate)", callback_data="login_escalate"),
                types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_forgot_{portal.lower()}")
            )

            bot.send_message(cid,
                "📩 **Reset Link / OTP Not Received**\n\n"
                "Please check:\n\n"
                "1️⃣ Check your **Spam / Junk** folder\n"
                "2️⃣ Wait **2–3 minutes** before requesting again\n"
                "3️⃣ Ensure you entered the correct email ID\n\n"
                "⚠️ *Too many requests may temporarily block delivery.*",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # --------------------------------------------------
        # FLOW D: Other Login Issue
        # --------------------------------------------------
        elif data.startswith("login_other_"):
            portal = data.split("_")[-1].capitalize()
            user_login_other_mode[cid] = portal
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data=f"login_portal_{portal.lower()}"))

            bot.send_message(cid,
                f"❓ **Other Login Issue — {portal}**\n\n"
                "Please briefly describe the login issue you are facing.\n"
                "Our AI will analyze and provide help.\n\n"
                "_(This is only for login-related issues)_",
                parse_mode="Markdown",
                reply_markup=markup
            )

        # --------------------------------------------------
        # Escalate to Support
        # --------------------------------------------------
        elif data == "login_escalate":
            bot.send_message(cid,
                "📞 **Escalated to Support**\n\n"
                "Your login issue has been noted.\n"
                "Our support team will assist you.\n\n"
                "📧 If urgent, please email: support@cpbfi.org\n\n"
                "Thank you for your patience! 🙏"
            )
            send_support_menu(bot, cid)

        # --------------------------------------------------
        # Fixed / Success
        # --------------------------------------------------
        elif data == "login_fixed":
            bot.send_message(cid, "🎉 Great! Your login issue is resolved.\n\nHappy learning! 📚")
            send_support_menu(bot, cid)

        # --------------------------------------------------
        # Back to Main Menu
        # --------------------------------------------------
        elif data == "login_back_menu":
            send_support_menu(bot, cid)


def is_in_login_other_mode(chat_id):
    """Check if user is in 'Other Login Issue' mode."""
    return user_login_other_mode.get(chat_id) is not None


def handle_login_other_message(bot, message):
    """Handle free-text input for 'Other Login Issue'."""
    cid = message.chat.id
    portal = user_login_other_mode.get(cid)
    user_query = message.text

    bot.send_chat_action(cid, "typing")
    
    # Use AI to respond to login issue
    prompt = f"User is facing a login issue on {portal} portal. Their issue: {user_query}"
    ai_response = ask_ai_free(prompt)
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("✅ Issue Resolved", callback_data="login_fixed"),
        types.InlineKeyboardButton("❓ Still Need Help", callback_data="login_escalate"),
        types.InlineKeyboardButton("⬅️ Back to Login Menu", callback_data="login")
    )
    
    bot.send_message(cid, ai_response, reply_markup=markup)
    
    # Clear the mode
    user_login_other_mode[cid] = None


def get_login_other_portal(chat_id):
    """Get the portal for 'Other Login Issue' mode."""
    return user_login_other_mode.get(chat_id)
