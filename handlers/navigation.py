from telebot import types
from handlers.menu import send_support_menu


def register(bot):
    """Register Navigation Help callback handlers."""

    @bot.callback_query_handler(func=lambda call: call.data.startswith("navhelp") or call.data.startswith("nav_"))
    def handle_navhelp(call):
        bot.answer_callback_query(call.id)
        cid = call.message.chat.id
        data = call.data

        if data == "navhelp":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("How to Use Platform (Student)", callback_data="nav_student"),
                types.InlineKeyboardButton("⬅️ Back to Main Menu", callback_data="nav_back_menu")
            )

            bot.send_message(cid,
                "**Navigation Help**\n\n"
                "Select a guide to learn how to use the platform:",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "nav_student":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(
                types.InlineKeyboardButton("How to Login", callback_data="nav_how_login"),
                types.InlineKeyboardButton("How to Attempt PCQ", callback_data="nav_how_pcq"),
                types.InlineKeyboardButton("How to Attempt Post Assessment", callback_data="nav_how_post"),
                types.InlineKeyboardButton("How to Submit Feedback", callback_data="nav_how_feedback"),
                types.InlineKeyboardButton("How to Complete Profile", callback_data="nav_how_profile"),
                types.InlineKeyboardButton("How to Download HR Certificate", callback_data="nav_how_hr_cert"),
                types.InlineKeyboardButton("How to Download Completion Certificate", callback_data="nav_how_comp_cert"),
                types.InlineKeyboardButton("⬅️ Back", callback_data="navhelp")
            )

            bot.send_message(cid,
                "**How to Use Platform — Student Guide**\n\n"
                "Select what you want to learn:",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "nav_how_login":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="nav_student"))

            bot.send_message(cid,
                "**How to Login**\n\n"
                "1. Open the student portal\n"
                "2. Enter your Student ID and Password\n"
                "3. Click on Login\n"
                "4. You will land on the Dashboard\n\n"
                "You're logged in!",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "nav_how_pcq":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="nav_student"))

            bot.send_message(cid,
                "**How to Attempt PCQ**\n\n"
                "1. Login to the student portal\n"
                "2. You will land on the Dashboard\n"
                "3. Scroll down on the dashboard\n"
                "4. Look for the Session cards\n"
                "5. Click on your Mobilization Session\n"
                "6. Inside the session, click on PCQ\n"
                "7. Click on Begin PCQ\n"
                "8. Answer all questions\n"
                "9. Click Submit\n"
                "10. Your PCQ score will be displayed\n\n"
                "PCQ completed successfully!",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "nav_how_post":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="nav_student"))

            bot.send_message(cid,
                "**How to Attempt Post Assessment**\n\n"
                "1. Login to the portal\n"
                "2. Go to Dashboard\n"
                "3. Scroll and open your Mobilization Session\n"
                "4. Click on Post Assessment\n"
                "5. Click Begin\n"
                "6. Submit the assessment\n"
                "7. View your score\n\n"
                "Post Assessment completed!",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "nav_how_feedback":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="nav_student"))

            bot.send_message(cid,
                "**How to Submit Feedback**\n\n"
                "1. Login to the portal\n"
                "2. Go to Dashboard\n"
                "3. Scroll to the last session card\n"
                "4. Click on Feedback\n"
                "5. Click Begin\n"
                "6. Fill the feedback form\n"
                "7. Click Submit\n\n"
                "Feedback submitted successfully!",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "nav_how_profile":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="nav_student"))

            bot.send_message(cid,
                "**How to Complete Your Profile**\n\n"
                "1. Login to the portal\n"
                "2. After login, you will be redirected to Profile\n"
                "3. Complete Basic Details\n"
                "4. Click Save & Continue\n"
                "5. Complete Advanced Details\n"
                "6. Click Save & Continue\n"
                "7. Complete Resume Details\n"
                "8. Click Save\n"
                "9. You will be redirected to Dashboard\n\n"
                "Profile completed successfully!",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "nav_how_hr_cert":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="nav_student"))

            bot.send_message(cid,
                "**How to Download HR Certificate**\n\n"
                "1. Login to the portal\n"
                "2. Go to Dashboard\n"
                "3. Scroll down\n"
                "4. Click on Certificates section\n"
                "5. Click on HR Certificate\n"
                "6. Certificate will download automatically\n\n"
                "HR Certificate downloaded!",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "nav_how_comp_cert":
            markup = types.InlineKeyboardMarkup(row_width=1)
            markup.add(types.InlineKeyboardButton("⬅️ Back", callback_data="nav_student"))

            bot.send_message(cid,
                "**How to Download Completion Certificate**\n\n"
                "1. Login to the portal\n"
                "2. Go to Dashboard\n"
                "3. Scroll down\n"
                "4. Click on Certificates section\n"
                "5. Click on Completion Certificate\n"
                "6. Certificate will download automatically\n\n"
                "Completion Certificate downloaded!",
                parse_mode="Markdown",
                reply_markup=markup
            )

        elif data == "nav_back_menu":
            send_support_menu(bot, cid)
