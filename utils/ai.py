import os
from groq import Groq
from dotenv import load_dotenv
from utils.prompts import SYSTEM_PROMPT, HUMAN_CHAT_PROMPT

load_dotenv()

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def ask_ai_free(prompt, human_mode=False):
    """Get AI response using Groq's free tier."""
    try:
        system = HUMAN_CHAT_PROMPT if human_mode else SYSTEM_PROMPT
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print("AI error:", e)
        return "AI system is unavailable right now."
