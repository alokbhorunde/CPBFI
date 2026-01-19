from handlers import pcq, other, ai_chat, login
from utils.ai import ask_ai_free


def register(bot):
    """Register catch-all message handlers for private chats."""
    
    @bot.message_handler(func=lambda msg: msg.chat.type == "private")
    def general_message_handler(message):
        cid = message.chat.id
        user_msg = message.text.lower() if message.text else ""
        
        # Check if user is in "Other Login Issue" mode
        if login.is_in_login_other_mode(cid):
            login.handle_login_other_message(bot, message)
            return
        
        # Check if user is in PCQ timing mode
        if pcq.is_in_timing_mode(cid):
            pcq.handle_timing_response(bot, message)
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
        
        # Check for PCQ 30-min timing keywords
        if pcq.check_pcq_timing_keywords(user_msg):
            pcq.start_timing_flow(bot, cid)
            return
        
        # Respond with AI for any other message
        ai_response = ask_ai_free(message.text)
        bot.send_message(cid, ai_response)
