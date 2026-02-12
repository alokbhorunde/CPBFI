![CI](https://github.com/alokbhorunde/CPBFI/actions/workflows/lint.yml/badge.svg)

# CPBFI Helpdesk Telegram Bot

A modular IT helpdesk support bot for the **CPBFI (Centre for Promotion of Banking and Financial Inclusion)** platform. It assists students with login issues, assessment problems (PCQ & Post Assessment), LMS/video troubleshooting, platform navigation, and general AI-powered support chat — all via Telegram.

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Project Structure](#project-structure)
- [Bot Flow](#bot-flow)
  - [Main Menu](#main-menu)
  - [Login Flow](#login-flow)
  - [Assessment Flow](#assessment-flow)
  - [LMS Flow](#lms-flow)
  - [Other Flows](#other-flows)
- [Escalation Mechanism](#escalation-mechanism)
- [AI Integration](#ai-integration)
- [Setup & Installation](#setup--installation)
- [Environment Variables](#environment-variables)
- [Running the Bot](#running-the-bot)
- [Deployment Guide](#deployment-guide)
- [Production Considerations](#production-considerations)
- [File-by-File Reference](#file-by-file-reference)
- [Troubleshooting](#troubleshooting)

---

## Architecture Overview

```
┌──────────────────────────────────────────────────┐
│                   Telegram API                    │
└──────────────────┬───────────────────────────────┘
                   │
          ┌────────▼────────┐
          │     main.py     │  ← Entry point, env validation, handler registration
          └────────┬────────┘
                   │
     ┌─────────────┼──────────────────────┐
     │             │                      │
     ▼             ▼                      ▼
┌─────────┐  ┌──────────┐          ┌──────────┐
│handlers/│  │handlers/ │   ...    │  utils/   │
│login.py │  │assess... │          │  ai.py    │
│         │  │          │          │  email.py │
└─────────┘  └──────────┘          │  prompts  │
                                   │  valid... │
                                   └──────────┘
```

**Key design decisions:**

- **Modular handlers** — Each support category (login, assessment, LMS, etc.) is a separate file with its own `register(bot)` function.
- **No database** — All user state is stored in in-memory Python dictionaries (e.g., `user_escalation_attempts`, `user_detail_collection`). State resets on bot restart.
- **AI-powered fallback** — When troubleshooting steps fail, AI (Groq/Llama) provides contextual help before escalation.
- **Email escalation** — When a user exhausts troubleshooting attempts (2+), the bot collects their details and emails the IT support team.

---

## Project Structure

```
cpbfi-bot/
├── main.py                  # Entry point — env validation, logging, handler registration
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (secrets — NOT in git)
├── .env.example             # Template for .env
├── .gitignore
│
├── handlers/                # All Telegram message/callback handlers
│   ├── __init__.py
│   ├── menu.py              # Main support menu (shared by all handlers)
│   ├── login.py             # Login issue flow (Skillserv / Knowlens)
│   ├── assessment.py        # Assessment issues (PCQ + Post Assessment)
│   ├── lms.py               # LMS / Videos issues
│   ├── navigation.py        # Platform navigation help
│   ├── other.py             # "Other Issue" — AI-assisted
│   ├── ai_chat.py           # Free-form AI chat mode
│   ├── help.py              # /help command & group message handler
│   ├── photo.py             # Screenshot/photo handler
│   └── general.py           # Catch-all for private messages + state routing
│
└── utils/                   # Shared utilities
    ├── __init__.py
    ├── ai.py                # Groq AI integration (with rate limit retry)
    ├── email.py             # SMTP email sender for escalation
    ├── prompts.py           # AI system prompts (SYSTEM_PROMPT, HUMAN_CHAT_PROMPT)
    └── validators.py        # Input validators (email format)
```

---

## Bot Flow

### Main Menu

When a user starts the bot or sends "hi/hello/menu/start", they see:

```
┌─────────────────────────────────┐
│      CPBFI Helpdesk             │
├─────────────┬───────────────────┤
│   Login     │   Assessment      │
├─────────────┼───────────────────┤
│   LMS       │   Navigation Help │
├─────────────┼───────────────────┤
│ Other Issue │                   │
├─────────────┴───────────────────┤
│        Chat with Us             │
└─────────────────────────────────┘
```

### Login Flow

```
Main Menu
  └── Login Issue
       ├── Skillserv Portal ─┐
       └── Knowlens Portal  ─┤
                              └── Select Issue Type
                                   ├── Invalid/Wrong Credentials → Tips → Still Not Working?
                                   ├── OTP Not Received           → Tips → Still Not Received?
                                   ├── Forgot Password            → Tips → Still Facing Issue?
                                   └── Other Login Issue           → AI analyzes user's description
                                                                          │
                                                     ┌─────────────────────┘
                                                     ▼
                                        "Still Not Working" counter
                                           Attempt 1 → more tips
                                           Attempt 2 → ESCALATION
                                                         │
                                                         ▼
                                              Collect: Name → Email → BFSI ID
                                              Send email to IT team
                                              Show confirmation
```

### Assessment Flow

```
Main Menu
  └── Assessment Issues (Skillserv)
       ├── Pre-Course Quiz (PCQ)
       │    ├── Where is the Quiz?
       │    ├── Test Not Showing
       │    ├── Unable to Submit
       │    ├── Exited Midway
       │    ├── Joined Late
       │    └── Other PCQ Issue → AI help
       │
       └── Post Assessment
            ├── Assessment Not Visible
            ├── Test Not Loading
            ├── Unable to Submit
            ├── Exited Midway
            ├── Time Window Issue
            └── Other Post Assessment Issue → AI help

       All sub-issues → "Still Not Working?" → Escalation after 2 attempts
       (same Name → Email → BFSI ID collection)
```

### LMS Flow

```
Main Menu
  └── LMS / Videos Issue
       ├── Batch Videos Not Visible
       ├── Videos Not Playing
       ├── Progress / Completion Not Updated
       ├── Course Expired / Access Duration
       └── Other LMS Issue → AI help

       All sub-issues → "Still Not Working?" → Escalation after 2 attempts
```

### Other Flows

| Flow | Handler | Description |
|------|---------|-------------|
| **Other Issue** | `other.py` | User describes issue → AI reply → Resolved? / Still Need Help / Main Menu |
| **Chat with Us** | `ai_chat.py` | Free-form AI chat (CPBFI-only questions). Exit button after every reply. |
| **Navigation Help** | `navigation.py` | Step-by-step platform usage guide for students |
| **Help (Groups)** | `help.py` | Typing "help" in a group → bot DMs the user with the support menu |
| **Photo/Screenshot** | `photo.py` | Bot analyzes caption keywords and gives relevant tips |

---

## Escalation Mechanism

The escalation system is the most critical part of the bot:

1. **Counter tracking** — Each handler tracks escalation attempts per user in a dictionary:
   - `user_escalation_attempts` (login)
   - `user_assessment_escalation_attempts` (assessment)
   - `user_lms_escalation_attempts` (lms)

2. **Threshold** — After **2 "Still Not Working" clicks**, the bot triggers detail collection.

3. **Detail collection** — A 3-step form:
   - Step 1: Full Name
   - Step 2: Email ID (validated with regex)
   - Step 3: BFSI ID

4. **Email dispatch** — Details are sent to the IT team via SMTP (Gmail). If the email fails, the user sees a fallback message with direct contact info.

5. **Counter preservation** — Counters are NOT reset when navigating back to menus (only when explicitly resolved or after successful escalation).

> **Important:** State is in-memory. If the bot restarts, all counters and in-progress collections are lost.

---

## AI Integration

The bot uses **Groq's free tier** with the `llama-3.1-8b-instant` model.

| Mode | System Prompt | Used In |
|------|--------------|---------|
| `SYSTEM_PROMPT` | IT helpdesk persona — short, focused responses | "Other Issue" handlers, fallback in `general.py` |
| `HUMAN_CHAT_PROMPT` | CPBFI-only Q&A — rejects non-platform questions | "Chat with Us" (`ai_chat.py`) |

**Rate limit handling:** The AI module retries up to 3 times with exponential backoff (2s, 4s, 8s) on 429 errors.

**Prompts** are defined in `utils/prompts.py` — edit them to change AI behavior.

---

## Setup & Installation

### Prerequisites

- Python 3.10+
- A Telegram Bot Token (from [@BotFather](https://t.me/BotFather))
- A Groq API Key (free at [console.groq.com](https://console.groq.com))
- A Gmail account with App Password for email escalation

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/alokbhorunde/CPBFI.git
cd cpbfi-bot

# 2. Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/Mac

# 5. Edit .env with your credentials
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BOT_TOKEN` | ✅ Yes | Telegram bot token from @BotFather |
| `GROQ_API_KEY` | ✅ Yes | API key for Groq AI (free tier) |
| `SENDER_EMAIL` | ✅ Yes | Gmail address for sending escalation emails |
| `SENDER_PASSWORD` | ✅ Yes | Gmail App Password (NOT your regular password) |
| `RECEIVER_EMAIL` | ✅ Yes | IT support email that receives escalation emails |

### Getting a Gmail App Password

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable **2-Step Verification** if not already enabled
3. Go to **App passwords** → Select "Mail" → Generate
4. Use the 16-character password as `SENDER_PASSWORD`

---

## Running the Bot

```bash
python main.py
```

Expected output:
```
2026-02-11 12:00:00,000 [INFO] __main__: 🤖 Bot is running...
2026-02-11 12:00:00,001 [INFO] __main__: 📁 Using modular handler structure
```

> **⚠️ Only one instance can run at a time.** If you see a `409 Conflict` error, another instance is already running. Stop it first.

---

## Deployment Guide

### Option 1: VPS / Cloud Server (Recommended)

```bash
# On your server (Ubuntu example):
sudo apt update && sudo apt install python3 python3-pip python3-venv

git clone https://github.com/alokbhorunde/CPBFI.git
cd cpbfi-bot

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file with your credentials
nano .env

# Run with systemd (see below) or screen/tmux
python main.py
```

#### Systemd Service (for auto-restart)

Create `/etc/systemd/system/cpbfi-bot.service`:

```ini
[Unit]
Description=CPBFI Helpdesk Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/cpbfi-bot
Environment=PATH=/home/ubuntu/cpbfi-bot/venv/bin
ExecStart=/home/ubuntu/cpbfi-bot/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable cpbfi-bot
sudo systemctl start cpbfi-bot

# Check status
sudo systemctl status cpbfi-bot

# View logs
journalctl -u cpbfi-bot -f
```

### Option 2: PythonAnywhere (Free Tier)

1. Upload files to PythonAnywhere
2. Set up a scheduled task or always-on task (paid feature)
3. Install dependencies: `pip install -r requirements.txt`
4. Create `.env` file with credentials
5. Run `python main.py`

> **Note:** Free-tier PythonAnywhere may not support long-running processes.

---

## Production Considerations

### ⚠️ Critical Things to Know

| Concern | Current State | What to Do |
|---------|--------------|------------|
| **State persistence** | In-memory (lost on restart) | For production scale, migrate to Redis or SQLite |
| **Single instance only** | `infinity_polling()` conflicts with multiple instances | Run exactly ONE instance at a time |
| **Groq free tier limits** | 30 req/min, 14,400 req/day | Monitor usage; upgrade if traffic increases |
| **Gmail sending limits** | ~500 emails/day | Sufficient for support bot; use SendGrid/Mailgun for higher volume |
| **No authentication** | Any Telegram user can use the bot | Consider restricting to specific groups or user IDs if needed |
| **Logging** | Console-only via Python `logging` | For production, add file handler or ship to a log aggregator |
| **Error recovery** | `infinity_polling()` auto-reconnects | Use systemd `Restart=always` as an additional safety net |

### Security Checklist

- [ ] `.env` is in `.gitignore` (already configured ✅)
- [ ] Use Gmail **App Password**, not real password
- [ ] Never commit `BOT_TOKEN` or `GROQ_API_KEY` to git
- [ ] Review `RECEIVER_EMAIL` — ensure it goes to the correct IT team inbox
- [ ] Consider restricting bot to specific Telegram groups/users if needed

### Monitoring

Currently there is no external monitoring. For production, consider:

1. **Uptime monitoring** — Use [UptimeRobot](https://uptimerobot.com) or similar to ping the server
2. **Error alerts** — Integrate Python logging with email/Slack alerts for ERROR-level logs
3. **Usage metrics** — Track escalation email count, AI API usage, active users

---

## File-by-File Reference

### Entry Point

| File | Purpose |
|------|---------|
| `main.py` | Loads env vars, validates them, configures logging, initializes bot, registers all handlers in order, starts polling |

### Handlers

| File | Trigger | Purpose |
|------|---------|---------|
| `menu.py` | Called by other handlers | Renders the main support menu with 6 category buttons |
| `login.py` | `callback_data` starting with `"login"` | Full login troubleshooting flow for Skillserv and Knowlens portals |
| `assessment.py` | `callback_data` starting with `"assessment"`, `"pcq"`, or `"post"` | PCQ and Post Assessment troubleshooting |
| `lms.py` | `callback_data` starting with `"lms"` | LMS / Videos troubleshooting |
| `navigation.py` | `callback_data` starting with `"navhelp"` or `"nav_"` | Step-by-step platform usage guide |
| `other.py` | `callback_data` `"other"`, `"other_resolved"`, `"other_back_menu"` | Free-form issue → AI analysis → nav buttons |
| `ai_chat.py` | `callback_data` `"ai_chat"` or `"exit_ai_chat"` | Persistent AI chat mode (CPBFI-only) |
| `help.py` | Text message `"help"` (groups & DMs) | DMs user from group with support menu |
| `photo.py` | Photo messages in private chat | Analyzes caption keywords, provides tips |
| `general.py` | All other private text messages | Routes to active handler or falls back to AI |

### Utilities

| File | Purpose |
|------|---------|
| `ai.py` | Groq API wrapper with retry logic and rate limit handling |
| `email.py` | SMTP email sender (Gmail) — returns `True`/`False` for success/failure |
| `prompts.py` | AI system prompts defining bot personality and scope |
| `validators.py` | Email format validation using regex |

---

## Handler Registration Order

The order in `main.py` matters — **more specific handlers must be registered first**:

```python
# 1. Callback handlers (button clicks) — order doesn't matter much
login.register(bot)
assessment.register(bot)
lms.register(bot)
navigation.register(bot)
other.register(bot)
ai_chat.register(bot)

# 2. Message handlers — ORDER MATTERS
photo.register(bot)     # Photo messages first
help.register(bot)      # "help" keyword handler
general.register(bot)   # Catch-all MUST be LAST
```

> **⚠️ `general.py` must always be registered last.** It's a catch-all that handles any private text message. If registered before other text handlers, it will intercept their messages.

---

## Message Routing in `general.py`

When a private text message arrives, `general.py` checks states in this order:

```
1. Is it a greeting? (hi/hello/start/menu) → Show main menu
2. Is user in login detail collection?      → Route to login handler
3. Is user in assessment detail collection? → Route to assessment handler
4. Is user in LMS detail collection?        → Route to LMS handler
5. Is user in login "other" mode?           → Route to login AI
6. Is user in assessment "other" mode?      → Route to assessment AI
7. Is user in LMS "other" mode?             → Route to LMS AI
8. Is user in "other issue" AI mode?        → Route to other handler
9. Is user in AI chat mode?                 → Route to AI chat
10. Fallback                                → AI responds + show menu
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `409 Conflict` error | Another bot instance is running | Stop the other instance first |
| `BOT_TOKEN is not set` | Missing `.env` file or variable | Create `.env` from `.env.example` |
| Emails not sending | Wrong `SENDER_PASSWORD` or Gmail security | Use App Password, enable 2FA |
| AI returns "unavailable" | Groq rate limit or API key issue | Check `GROQ_API_KEY`, wait if rate limited |
| Bot not responding in groups | Bot privacy mode is ON | Talk to @BotFather → `/setprivacy` → Disable |
| Buttons show loading spinner | Missing `answer_callback_query` | Already fixed — ensure latest code is deployed |

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `pyTelegramBotAPI` | 4.14.0 | Telegram Bot API wrapper (telebot) |
| `groq` | 0.9.0 | Groq AI API client |
| `httpx` | 0.27.0 | HTTP client (dependency of groq) |
| `python-dotenv` | 1.0.1 | Load `.env` file into environment |

---

## Future Improvements

If continuing development, consider:

1. **Database** — Replace in-memory dicts with SQLite/PostgreSQL for state persistence across restarts
2. **Webhook mode** — Switch from polling to webhook for better performance on production servers
3. **Admin panel** — Add `/admin` commands for viewing escalation stats, user counts
4. **Multi-language** — Add Hindi/regional language support for CPBFI's diverse user base
5. **Rate limiting** — Add per-user rate limiting to prevent abuse
6. **Metrics dashboard** — Track resolution rates, escalation frequency, AI usage

---

*Last updated: February 2026*
*Developed for CPBFI IT Support Team*
