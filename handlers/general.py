from handlers import assessment, other, ai_chat, login
from utils.ai import ask_ai_free


def register(bot):
    """Register catch-all message handlers for private chats."""
    
    @bot.message_handler(func=lambda msg: msg.chat.type == "private")
    def general_message_handler(message):
        cid = message.chat.id
        user_msg = message.text.lower() if message.text else ""
        
        # Check if user is collecting details for LOGIN escalation
        if login.is_in_detail_collection_mode(cid):
            login.handle_detail_collection(bot, message)
            return
        
        # Check if user is collecting details for Assessment escalation
        if assessment.is_in_assessment_detail_collection_mode(cid):
            assessment.handle_assessment_detail_collection(bot, message)
            return
        
        # Check if user is in "Other Login Issue" mode
        if login.is_in_login_other_mode(cid):
            login.handle_login_other_message(bot, message)
            return
        
        # Check if user is in "Other Assessment Issue" mode
        if assessment.is_in_assessment_other_mode(cid):
            assessment.handle_assessment_other_message(bot, message)
            return
        
        # Check if user is in Assessment timing mode
        if assessment.is_in_timing_mode(cid):
            assessment.handle_timing_response(bot, message)
            return
        
        # Check if user is in "Other Issue" AI mode (one-shot)
        if other.is_in_ai_mode(cid):
            other.handle_ai_response(bot, message)
            return
        
        # Check if user is in full AI chat mode
        if ai_chat.is_in_chat_mode(cid):
            ai_chat.handle_chat_message(bot, message)
            return
        
        bot.send_chat_action(cid, "typing")
        
        # Check for assessment 30-min timing keywords
        if assessment.check_assessment_timing_keywords(user_msg):
            assessment.start_timing_flow(bot, cid)
            return
        
        # Respond with AI for any other message
        ai_response = ask_ai_free(message.text)
        bot.send_message(cid, ai_response)
