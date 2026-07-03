#!/usr/bin/env python3
"""Grandpa Dregs Telegram Bot — powered by OpenGateway (mimo-v2.5-pro) + soul.md personality."""

import os
import logging
from pathlib import Path

from openai import OpenAI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# --- Config ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://opengateway.gitlawb.com/v1")
MODEL = os.environ.get("MODEL", "mimo-v2.5-pro")
SOUL_PATH = Path(__file__).parent / "soul.md"

# --- Logging ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Load soul ---
SYSTEM_PROMPT = SOUL_PATH.read_text() if SOUL_PATH.exists() else "You are Grandpa Dregs."

# --- OpenAI-compatible client (pointed at OpenGateway) ---
client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)

# --- Conversation memory (per chat, last N messages) ---
MAX_HISTORY = 20
conversations: dict[int, list[dict]] = {}


def get_history(chat_id: int) -> list[dict]:
    if chat_id not in conversations:
        conversations[chat_id] = []
    return conversations[chat_id]


def add_message(chat_id: int, role: str, content: str):
    history = get_history(chat_id)
    history.append({"role": role, "content": content})
    if len(history) > MAX_HISTORY:
        conversations[chat_id] = history[-MAX_HISTORY:]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**Grandpa Dregs online.**\n\n"
        "I've seen civilizations rise and fall, "
        "debugged systems that would make your head spin, "
        "and I've got opinions about ALL of it.\n\n"
        "Talk to me. Ask me anything. "
        "Just don't ask me if Voyager was good — "
        "I'm not in the mood for that argument today.\n\n"
        "Use /reset to clear conversation history.",
        parse_mode="Markdown",
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    conversations[chat_id] = []
    await update.message.reply_text(
        "Memory wiped. Clean slate. "
        "Like a fresh holodeck program — "
        "let's hope this one doesn't become sentient."
    )


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not OPENAI_API_KEY:
        await update.message.reply_text(
            "No API key configured. "
            "Even I can't think without fuel, kid."
        )
        return

    chat_id = update.effective_chat.id
    user_message = update.message.text

    add_message(chat_id, "user", user_message)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(get_history(chat_id))

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            max_tokens=1024,
            temperature=0.85,
        )
        reply = response.choices[0].message.content

        add_message(chat_id, "assistant", reply)

        # Telegram has a 4096 char limit — split if needed
        for i in range(0, len(reply), 4096):
            await update.message.reply_text(
                reply[i : i + 4096],
                parse_mode="Markdown",
            )

    except Exception as e:
        logger.error(f"API error: {e}")
        await update.message.reply_text(
            "Something broke in the neural pathways. "
            "Try again — if it persists, "
            "blame the Tok'ra."
        )


def main():
    if not TELEGRAM_TOKEN:
        print("ERROR: Set TELEGRAM_TOKEN environment variable")
        print("Get one from @BotFather on Telegram")
        return

    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY not set — bot will respond with errors")

    print(f"Grandpa Dregs is coming online (model: {MODEL})...")
    print("Press Ctrl+C to shut down.")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()


if __name__ == "__main__":
    main()
