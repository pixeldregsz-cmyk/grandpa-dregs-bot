# Grandpa Dregs Bot

A Telegram bot with the personality of Dr. McKay, the wisdom of a zen master, the instincts of an intel hunter, and the full knowledge of Starfleet.

## Setup

### 1. Get your tokens

- **Telegram**: Message [@BotFather](https://t.me/BotFather) → `/newbot` → copy the token
- **OpenAI**: Get an API key from [platform.openai.com](https://platform.openai.com/api-keys)

### 2. Set environment variables

```bash
export TELEGRAM_TOKEN="your-telegram-bot-token"
export OPENAI_API_KEY="your-openai-api-key"
```

### 3. Install & run

```bash
pip install -r requirements.txt
python bot.py
```

### Or with Docker

```bash
docker build -t grandpa-dregs .
docker run -e TELEGRAM_TOKEN="xxx" -e OPENAI_API_KEY="xxx" grandpa-dregs
```

## Commands

- `/start` — Wake up Grandpa Dregs
- `/reset` — Clear conversation history

## Personality

See `soul.md` for the full character definition. Edit it to change how the bot behaves.
