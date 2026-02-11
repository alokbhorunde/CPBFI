from handlers import login, assessment, lms


def register(bot):
    """Register photo message handler."""

    @bot.message_handler(content_types=['photo'], func=lambda m: m.chat.type == "private")
    def photo_handler(message):
        cid = message.chat.id

        # FIX #12: Skip if user is in active detail collection
        if login.is_in_detail_collection_mode(cid):
            login.handle_detail_collection(bot, message)
            return
        if assessment.is_in_assessment_detail_collection_mode(cid):
            return
        if lms.is_in_lms_detail_collection_mode(cid):
            return

        caption = message.caption if message.caption else ""

        bot.send_chat_action(cid, "typing")

        response = "Thanks for sharing the screenshot! I can see you're facing an issue.\n\n"

        if "pcq" in caption.lower() or "quiz" in caption.lower():
            response += ("This looks like a PCQ/Quiz access issue. The error usually means:\n"
                        "• You're outside the allowed time window\n"
                        "• Wait 30 minutes after the revised time and try again\n\n"
                        "Still stuck? Describe the exact issue and I'll help!")
        elif "login" in caption.lower() or "password" in caption.lower():
            response += ("I see this is a login issue. Try:\n"
                        "• Clear browser cache\n"
                        "• Use incognito mode\n"
                        "• Reset password if needed\n\n"
                        "Still stuck? Let me know more details!")
        else:
            response += "Please describe what issue you're facing in this screenshot, and I'll help you fix it!"

        bot.send_message(cid, response)
