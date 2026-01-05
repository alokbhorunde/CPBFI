# CPBFI Support Bot

A Telegram support bot with AI-powered assistance using Groq.

## Features

- 🔐 Login Help
- 📝 PCQ Support
- 🧪 Post Assessment Help
- 📘 LMS Assistance
- 📱 Navigation Help
- 💬 AI Chat Assistant (powered by Groq)

## Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your credentials:
   ```
   BOT_TOKEN=your_telegram_bot_token
   GROQ_API_KEY=your_groq_api_key
   SENDER_EMAIL=your_email
   SENDER_PASSWORD=your_app_password
   RECEIVER_EMAIL=it_support_email
   ```
4. Run the bot:
   ```bash
   python main.py
   ```

## Deployment

### Railway / Render / Heroku

1. Push to GitHub (without `.env`)
2. Set environment variables in the platform dashboard
3. Deploy

### VPS

1. Clone repo on server
2. Create `.env` file
3. Run with: `python main.py` or use `pm2` / `systemd`

## ⚠️ Important

**Never push `.env` to Git!** It contains sensitive API keys.
