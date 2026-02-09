# 🤖 CPBFI Helpdesk Telegram Bot

A professional, AI-powered Telegram bot for student support at CPBFI (Centre for Promotion of Banking, Finance & Insurance). The bot provides instant assistance for login issues, assessments, LMS navigation, and more.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Handlers Documentation](#-handlers-documentation)
- [Utilities Documentation](#-utilities-documentation)
- [Bot Flows](#-bot-flows)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Login Support** | Troubleshooting for Skillserv & Knowlens portal access |
| 📚 **Assessment Help** | PCQ and Post Assessment issue resolution |
| 📖 **LMS Assistance** | Video playback, progress tracking, course access |
| 🧭 **Navigation Guides** | Step-by-step platform tutorials for students |
| 🤖 **AI Chat** | Groq-powered AI for CPBFI-specific queries |
| 📧 **Auto-Escalation** | Smart escalation with email notifications to IT |
| 📷 **Screenshot Analysis** | Caption-based troubleshooting from screenshots |
| 👥 **Group Support** | Works in groups with DM-based interaction |

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          TELEGRAM API                          │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                          main.py                                │
│                    (Bot Initialization)                         │
└─────────────────────────────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    HANDLERS     │    │     UTILS       │    │   EXTERNAL      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • login.py      │    │ • ai.py         │    │ • Groq API      │
│ • assessment.py │    │ • email.py      │    │ • Gmail SMTP    │
│ • lms.py        │    │ • prompts.py    │    │                 │
│ • navigation.py │    │                 │    │                 │
│ • ai_chat.py    │    │                 │    │                 │
│ • other.py      │    │                 │    │                 │
│ • photo.py      │    │                 │    │                 │
│ • help.py       │    │                 │    │                 │
│ • general.py    │    │                 │    │                 │
│ • menu.py       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

---

## 🚀 Installation

### Prerequisites

- Python 3.8+
- Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- Groq API Key (for AI features)
- Gmail App Password (for email escalation)

### Setup

```bash
# Clone the repository
git clone https://github.com/alokbhorunde/CPBFI.git
cd CPBFI

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your credentials

# Run the bot
python main.py
```

---

## ⚙ Configuration

Create a `.env` file with the following variables:

```env
# Telegram Bot
BOT_TOKEN=your_telegram_bot_token

# Groq AI
GROQ_API_KEY=your_groq_api_key

# Email Configuration (for escalation)
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_app_password
RECEIVER_EMAIL=it_support@company.com
```

---

## 📁 Project Structure

```
cpbfi-bot/
├── main.py                 # Entry point, bot initialization
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .gitignore             # Git ignore rules
│
├── handlers/              # All message & callback handlers
│   ├── __init__.py        # Package initialization
│   ├── menu.py            # Main support menu
│   ├── login.py           # Login issue handling
│   ├── assessment.py      # PCQ & Post Assessment flows
│   ├── lms.py             # LMS & video issues
│   ├── navigation.py      # Platform navigation guides
│   ├── ai_chat.py         # Continuous AI chat mode
│   ├── other.py           # One-shot AI for misc issues
│   ├── photo.py           # Screenshot/photo processing
│   ├── help.py            # /help command (groups + DMs)
│   └── general.py         # Catch-all message router
│
└── utils/                 # Utility modules
    ├── __init__.py        # Package initialization
    ├── ai.py              # Groq API integration
    ├── email.py           # Email notification system
    └── prompts.py         # AI system prompts
```

---

## 📚 Handlers Documentation

### 1. `main.py` - Entry Point

**Purpose:** Initializes the bot and registers all handlers in the correct order.

```python
# Handler registration order (important!)
1. login.register(bot)      # Login callbacks
2. assessment.register(bot) # Assessment callbacks
3. lms.register(bot)        # LMS callbacks
4. navigation.register(bot) # Navigation callbacks
5. other.register(bot)      # Other issue callbacks
6. ai_chat.register(bot)    # AI chat callbacks
7. photo.register(bot)      # Photo messages
8. help.register(bot)       # /help command
9. general.register(bot)    # Catch-all (MUST BE LAST!)
```

---

### 2. `handlers/menu.py` - Main Menu

**Purpose:** Displays the main support category menu.

**Function:**
```python
send_support_menu(bot, chat_id)
```

**Menu Buttons:**
| Button | Callback Data |
|--------|---------------|
| 🔐 Login | `login` |
| 📚 Assessment | `assessment` |
| 📖 LMS | `lms` |
| 🧭 Navigation Help | `navhelp` |
| ❓ Other Issue | `other` |
| 💬 Chat with Us | `ai_chat` |

---

### 3. `handlers/login.py` - Login Issues

**Purpose:** Handles all login-related problems for Skillserv and Knowlens portals.

**Callback Prefixes:** `login*`

**Flow:**
```
login → Portal Selection → Issue Type → Solution → Fixed/Try Again/Escalate
```

**Key States:**
| State Variable | Purpose |
|----------------|---------|
| `user_login_other_mode` | Tracks users in "Other Login Issue" mode |
| `user_detail_collection` | Collects escalation details (name, email, BFSI ID) |
| `user_escalation_attempts` | Tracks retry attempts before escalation |

**Issue Types:**
- Invalid Credentials
- OTP Not Received
- Forgot Password
- Other Login Issue (AI-powered)

**Escalation Logic:**
- Attempt 1: Provide alternative solution
- Attempt 2+: Collect details → Send email to IT

---

### 4. `handlers/assessment.py` - Assessments

**Purpose:** Handles PCQ (Pre-Course Quiz) and Post Assessment issues.

**Callback Prefixes:** `assessment*`, `pcq*`, `post*`

**Flow:**
```
assessment → PCQ/Post → Issue Type → Solution/Time Calculator → Fixed/Escalate
```

**Special Features:**

**⏱️ PCQ Time Calculator:**
```python
# Checks if user is within 30-minute window
if time_difference <= 30:
    "You can still join!"
else:
    "Time has exceeded, contact IT"
```

**Issue Types (PCQ):**
- Where to find Quiz
- Test Not Showing
- Unable to Submit
- Exited Midway
- Time/Late Joining Issue
- Other PCQ Issue

**Issue Types (Post Assessment):**
- Assessment Not Visible
- Loading Issues
- Submission Failed
- Exited Midway
- Other Post Issue

---

### 5. `handlers/lms.py` - LMS Issues

**Purpose:** Handles Learning Management System related problems.

**Callback Prefixes:** `lms*`

**Flow:**
```
lms → Issue Type → Solution → Fixed/Escalate
```

**Issue Types:**
- Videos Not Visible
- Videos Not Playing
- Progress Not Updated
- Course Expired
- Other LMS Issue (AI-powered)

---

### 6. `handlers/navigation.py` - Platform Guides

**Purpose:** Provides step-by-step instructional guides for students.

**Callback Prefixes:** `navhelp*`, `nav_*`

**Flow:**
```
navhelp → Student Guide → Select Topic → View Instructions → Back
```

**7 Student Guides:**

| Guide | Steps |
|-------|-------|
| 🔐 How to Login | Portal → ID/Password → Login → Dashboard |
| 🧠 How to Attempt PCQ | Dashboard → Session → PCQ → Begin → Submit |
| 📊 How to Attempt Post Assessment | Dashboard → Session → Post → Begin → Submit |
| 📝 How to Submit Feedback | Dashboard → Session → Feedback → Submit |
| 👤 How to Complete Profile | Login → Basic → Advanced → Resume → Save |
| 🎓 How to Download HR Certificate | Dashboard → Certificates → HR → Download |
| 🏆 How to Download Completion Certificate | Dashboard → Certificates → Completion → Download |

---

### 7. `handlers/ai_chat.py` - AI Chat Mode

**Purpose:** Provides continuous AI-powered chat for CPBFI-related questions.

**Callback Data:** `ai_chat`, `exit_ai_chat`

**Key Features:**
- Restricted to CPBFI platform questions only
- Declines general knowledge, coding, weather, etc.
- Uses `human_mode=True` for friendly responses

**State Variable:**
```python
user_ai_chat_mode = {}  # {chat_id: True/False}
```

**Functions:**
```python
is_in_chat_mode(chat_id)      # Check if user is in AI chat
handle_chat_message(bot, msg) # Process AI chat messages
```

---

### 8. `handlers/other.py` - Other Issues

**Purpose:** One-shot AI response for miscellaneous platform issues.

**Callback Data:** `other`

**Flow:**
```
other → User describes issue → AI responds (once) → Exit mode
```

**State Variable:**
```python
user_other_mode = {}  # {chat_id: True/False}
```

---

### 9. `handlers/photo.py` - Screenshot Handler

**Purpose:** Processes screenshot captions for context-aware troubleshooting.

**Caption Keywords:**
| Keyword | Response Type |
|---------|---------------|
| `pcq` | PCQ troubleshooting tips |
| `login` | Login troubleshooting tips |
| (other) | General acknowledgment |

---

### 10. `handlers/help.py` - Help Command

**Purpose:** Handles `/help` command for both private chats and groups.

**Behavior:**

| Context | Action |
|---------|--------|
| Private Chat | Show main menu directly |
| Group Chat | DM user with menu + Reply in group with "Go to Chat" button |

---

### 11. `handlers/general.py` - Message Router

**Purpose:** Central message router that handles all private messages.

**⚠️ MUST BE REGISTERED LAST!**

**Greeting Keywords (Reset all states):**
```python
GREETING_KEYWORDS = ["hi", "hello", "hey", "start", "menu", "help", "home"]
```

**Routing Logic:**
```python
1. Check if greeting → Clear states → Show menu
2. Check if in AI chat mode → Route to ai_chat handler
3. Check if in other_issue mode → Route to other handler
4. Check if collecting login details → Route to login handler
5. Check if collecting assessment details → Route to assessment handler
6. Check if in login_other_mode → Route to login AI handler
7. Default: Prompt user to use menu
```

---

## 🔧 Utilities Documentation

### 1. `utils/ai.py` - AI Integration

**Purpose:** Integrates with Groq API for AI responses.

**Function:**
```python
def ask_ai_free(prompt, human_mode=False):
    """
    Get AI response from Groq.
    
    Args:
        prompt: User's question
        human_mode: True for friendly chat, False for formal support
    
    Returns:
        AI response string
    """
```

**Model:** `llama-3.1-8b-instant`

---

### 2. `utils/email.py` - Email Notifications

**Purpose:** Sends escalation emails to IT support team.

**Function:**
```python
def send_email_to_it(user_data, issue):
    """
    Send escalation email to IT team.
    
    Args:
        user_data: Dict with name, email, bfsi_id
        issue: Description of the issue
    """
```

**SMTP Configuration:** Gmail with App Password

---

### 3. `utils/prompts.py` - AI Prompts

**Purpose:** Defines system prompts for AI behavior.

**Prompts:**

| Prompt | Usage |
|--------|-------|
| `SYSTEM_PROMPT` | Formal IT support responses |
| `HUMAN_CHAT_PROMPT` | Friendly chat (CPBFI-only, restricted) |

**HUMAN_CHAT_PROMPT Restrictions:**
- ✅ Login, Assessment, LMS, Navigation, Profile, Certificates, Feedback
- ❌ General knowledge, coding, weather, jokes, etc.

---

## 🔄 Bot Flows

### Main Flow
```
User Message → general.py routes → Specific Handler → Solution/Escalation → Menu
```

### Escalation Flow
```
Issue → Solution → "Still Not Working?" → Attempt 1 (Try Again) → Attempt 2+ → 
Collect Details (Name → Email → BFSI ID) → Send Email → Confirm → Menu
```

### AI Chat Flow
```
"Chat with Us" → Enter AI Mode → User asks question → AI responds → 
Loop until "Exit AI Chat" → Return to Menu
```

---

## 📡 API Reference

### Telegram Bot API

| Method | Usage |
|--------|-------|
| `bot.send_message()` | Send text messages |
| `bot.send_chat_action()` | Show "typing..." |
| `bot.callback_query_handler()` | Handle button clicks |
| `bot.message_handler()` | Handle text messages |

### Groq API

| Endpoint | Model |
|----------|-------|
| `chat.completions.create()` | `llama-3.1-8b-instant` |

### Gmail SMTP

| Parameter | Value |
|-----------|-------|
| Host | `smtp.gmail.com` |
| Port | `587` |
| Auth | App Password |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m "Add new feature"`
4. Push to branch: `git push origin feature/new-feature`
5. Open a Pull Request

---

## 📄 License

This project is proprietary software for CPBFI internal use.

---

## 👨‍💻 Author

**CPBFI IT Team**

- GitHub: [@alokbhorunde](https://github.com/alokbhorunde)
- Repository: [CPBFI Bot](https://github.com/alokbhorunde/CPBFI)

---

*Last Updated: February 2026*
