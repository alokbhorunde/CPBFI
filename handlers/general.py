from handlers import assessment, lms, other, ai_chat, login
from handlers.menu import send_support_menu
from utils.ai import ask_ai_free

# Greeting keywords that reset all flows and show main menu
GREETING_KEYWORDS = ["hi", "hello", "hey", "start", "menu", "help", "main menu", "home"]


def clear_all_user_states(cid):
    """Clear all user states for a given chat ID."""
    # Clear login states
    if cid in login.user_login_other_mode:
        login.user_login_other_mode[cid] = None
    if cid in login.user_escalation_attempts:
        login.user_escalation_attempts[cid] = {"count": 0, "portal": "", "issue": ""}
    if cid in login.user_detail_collection:
        del login.user_detail_collection[cid]
    
    # Clear assessment states
    if cid in assessment.user_assessment_other_mode:
        assessment.user_assessment_other_mode[cid] = {"active": False, "type": ""}
    if cid in assessment.user_assessment_escalation_attempts:
        assessment.user_assessment_escalation_attempts[cid] = {"count": 0, "issue": "", "type": ""}
    if cid in assessment.user_assessment_detail_collection:
        del assessment.user_assessment_detail_collection[cid]
    if cid in assessment.user_assessment_timing:
        assessment.user_assessment_timing[cid] = False
    
    # Clear LMS states
    if cid in lms.user_lms_other_mode:
        lms.user_lms_other_mode[cid] = False
    if cid in lms.user_lms_escalation_attempts:
        lms.user_lms_escalation_attempts[cid] = {"count": 0, "issue": ""}
    if cid in lms.user_lms_detail_collection:
        del lms.user_lms_detail_collection[cid]
    
    # Clear other issue states
    if cid in other.user_ai_mode:
        other.user_ai_mode[cid] = False
    
    # Clear AI chat states
    if cid in ai_chat.user_ai_chat_mode:
        ai_chat.user_ai_chat_mode[cid] = False


def is_greeting(text):
    """Check if the message is a greeting that should reset flows."""
    text_lower = text.lower().strip()
    return text_lower in GREETING_KEYWORDS or text_lower.startswith("/start")


def register(bot):
    """Register catch-all message handlers for private chats."""
    
    @bot.message_handler(func=lambda msg: msg.chat.type == "private")
    def general_message_handler(message):
        cid = message.chat.id
        user_msg = message.text.lower() if message.text else ""
        
        # =====================================================
        # GREETING CHECK - Reset all flows and show main menu
        # =====================================================
        if message.text and is_greeting(message.text):
            clear_all_user_states(cid)
            bot.send_message(cid, "👋 Welcome to CPBFI Helpdesk!\n\nHow can I assist you today?")
            send_support_menu(bot, cid)
            return
        
        # Check if user is collecting details for LOGIN escalation
        if login.is_in_detail_collection_mode(cid):
            login.handle_detail_collection(bot, message)
            return
        
        # Check if user is collecting details for Assessment escalation
        if assessment.is_in_assessment_detail_collection_mode(cid):
            assessment.handle_assessment_detail_collection(bot, message)
            return
        
        # Check if user is collecting details for LMS escalation
        if lms.is_in_lms_detail_collection_mode(cid):
            lms.handle_lms_detail_collection(bot, message)
            return
        
        # Check if user is in "Other Login Issue" mode
        if login.is_in_login_other_mode(cid):
            login.handle_login_other_message(bot, message)
            return
        
        # Check if user is in "Other Assessment Issue" mode
        if assessment.is_in_assessment_other_mode(cid):
            assessment.handle_assessment_other_message(bot, message)
            return
        
        # Check if user is in "Other LMS Issue" mode
        if lms.is_in_lms_other_mode(cid):
            lms.handle_lms_other_message(bot, message)
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

